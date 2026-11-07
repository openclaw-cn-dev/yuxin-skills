"""
RKR 重复文档清理脚本 v2
- 纯 SQL 批量删除，避免 Python ORM 类型转换问题
- 保留规则：completed > uploaded > failed，同状态取最新
"""
import sys
sys.path.insert(0, '/app')
from sqlalchemy import text
from app.core.database import sync_session_maker

BATCH_SIZE = 1000

def main():
    db = sync_session_maker()
    db.execute(text("SET lock_timeout = '5s';"))
    db.commit()

    print("=" * 60)
    print("RKR 重复文档清理 v2")
    print("=" * 60)

    # 统计
    total = db.execute(text("SELECT COUNT(*) FROM documents")).scalar()
    unique = db.execute(text(
        "SELECT COUNT(DISTINCT original_filename) FROM documents"
    )).scalar()
    print(f"\n清理前: {total} 文档 | {unique} 唯一文件名 | {total - unique} 重复")

    if total == unique:
        print("没有重复文档，退出")
        db.close()
        return

    # 用纯 SQL 找重复组，标记每组要保留的文档
    # 保留规则: completed > uploaded > failed, 同状态保留最新的
    print("\n步骤1: 标记要保留的文档...")
    db.execute(text("""
        CREATE TEMP TABLE IF NOT EXISTS dup_keepers AS
        SELECT DISTINCT ON (original_filename)
            id, original_filename
        FROM documents
        WHERE original_filename IN (
            SELECT original_filename FROM documents
            GROUP BY original_filename HAVING COUNT(*) > 1
        )
        ORDER BY original_filename,
            CASE processing_status
                WHEN 'completed' THEN 1
                WHEN 'uploaded' THEN 2
                WHEN 'failed' THEN 3
                ELSE 99
            END,
            created_at DESC;
    """))
    db.commit()

    keeper_count = db.execute(text("SELECT COUNT(*) FROM dup_keepers")).scalar()
    print(f"  保留文档: {keeper_count}")

    # 找出要删除的 ID
    print("\n步骤2: 找出要删除的文档ID...")
    db.execute(text("""
        CREATE TEMP TABLE IF NOT EXISTS dup_to_delete AS
        SELECT d.id
        FROM documents d
        WHERE d.original_filename IN (
            SELECT original_filename FROM dup_keepers
        )
        AND d.id NOT IN (SELECT id FROM dup_keepers);
    """))
    db.commit()

    delete_count = db.execute(text("SELECT COUNT(*) FROM dup_to_delete")).scalar()
    print(f"  待删除: {delete_count}")

    if delete_count == 0:
        print("无重复文档需要删除，退出")
        db.close()
        return

    # 分批删除
    print(f"\n步骤3: 分批删除 (每批{BATCH_SIZE})...")
    total_batches = (delete_count + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(total_batches):
        offset = batch_num * BATCH_SIZE
        try:
            # 删除 document_chunks（vectors 有 ON DELETE CASCADE，自动删除）
            result = db.execute(text("""
                DELETE FROM document_chunks
                WHERE document_id IN (
                    SELECT id FROM dup_to_delete
                    ORDER BY id
                    LIMIT :limit OFFSET :offset
                )
            """), {"limit": BATCH_SIZE, "offset": offset})
            chunk_del = result.rowcount

            # 删除 documents
            result = db.execute(text("""
                DELETE FROM documents
                WHERE id IN (
                    SELECT id FROM dup_to_delete
                    ORDER BY id
                    LIMIT :limit OFFSET :offset
                )
            """), {"limit": BATCH_SIZE, "offset": offset})
            doc_del = result.rowcount

            db.commit()

            if (batch_num + 1) % 10 == 0 or batch_num == total_batches - 1:
                print(f"  批次 {batch_num + 1}/{total_batches}: "
                      f"删除 {doc_del} 文档, {chunk_del} 分段 "
                      f"(进度: {(batch_num + 1) * 100 // total_batches}%)")

        except Exception as e:
            db.rollback()
            print(f"  ✗ 批次 {batch_num + 1} 失败: {e}")
            continue

    # 清理临时表
    db.execute(text("DROP TABLE IF EXISTS dup_to_delete;"))
    db.execute(text("DROP TABLE IF EXISTS dup_keepers;"))
    db.commit()

    # 验证
    new_total = db.execute(text("SELECT COUNT(*) FROM documents")).scalar()
    new_unique = db.execute(text(
        "SELECT COUNT(DISTINCT original_filename) FROM documents"
    )).scalar()

    print(f"\n{'=' * 60}")
    print(f"清理完成!")
    print(f"  清理前: {total} 文档, {unique} 唯一")
    print(f"  清理后: {new_total} 文档, {new_unique} 唯一")
    print(f"  删除文档: {total - new_total}")
    print(f"{'=' * 60}")

    # 各状态分布
    statuses = db.execute(text("""
        SELECT processing_status, COUNT(*) FROM documents GROUP BY processing_status
    """)).fetchall()
    print("\n当前状态分布:")
    for row in statuses:
        print(f"  {row[0]}: {row[1]}")

    db.close()


if __name__ == "__main__":
    main()
