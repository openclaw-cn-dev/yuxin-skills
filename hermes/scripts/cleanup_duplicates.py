"""
RKR 重复文档清理脚本 v1
- 按 original_filename 分组去重
- 保留规则：completed > uploaded > failed > 最新
- 先删除子表（vectors, document_chunks），再删主表
- 批量执行，每批 1000 条
"""
import sys
sys.path.insert(0, '/app')

import uuid
from sqlalchemy import text, select, func, and_
from app.core.database import sync_session_maker
from app.models.document import Document

STATUS_PRIORITY = {"completed": 0, "uploaded": 1, "failed": 2}
BATCH_SIZE = 1000

def main():
    db = sync_session_maker()

    print("=" * 60)
    print("RKR 重复文档清理")
    print("=" * 60)

    # ── 1. 统计 ──
    total = db.execute(text("SELECT COUNT(*) FROM documents")).scalar()
    unique = db.execute(text(
        "SELECT COUNT(DISTINCT original_filename) FROM documents"
    )).scalar()
    dup_count = total - unique
    print(f"\n总文档: {total}")
    print(f"唯一文件名: {unique}")
    print(f"重复文档: {dup_count} ({dup_count*100//total}%)")

    if dup_count == 0:
        print("没有重复文档，无需清理")
        db.close()
        return

    # ── 2. 找出所有重复组 ──
    print("\n正在分析重复组...")
    dup_groups = db.execute(text("""
        SELECT original_filename, COUNT(*) as cnt
        FROM documents
        GROUP BY original_filename
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """)).fetchall()

    print(f"重复文件名组: {len(dup_groups)}")

    # ── 3. 确定每组保留哪个 ──
    keep_ids = []
    delete_ids = []

    for group in dup_groups:
        filename = group[0]

        # 查找该文件名下的所有文档
        docs = db.execute(
            select(Document).where(Document.original_filename == filename)
            .order_by(Document.created_at.desc())
        ).scalars().all()

        if len(docs) <= 1:
            continue

        # 按优先级排序：completed > uploaded > failed，同状态取最新
        def sort_key(doc):
            priority = STATUS_PRIORITY.get(doc.processing_status, 99)
            return (priority, -doc.created_at.timestamp())

        docs.sort(key=lambda d: (
            STATUS_PRIORITY.get(d.processing_status, 99),
        ))

        # 保留第一个（最优的），其余标记删除
        keep_ids.append(str(docs[0].id))
        for doc in docs[1:]:
            delete_ids.append(str(doc.id))

    print(f"保留: {len(keep_ids)}")
    print(f"待删除: {len(delete_ids)}")

    # ── 4. 分批删除 ──
    print(f"\n开始分批删除 (每批 {BATCH_SIZE})...")

    total_deleted = 0
    total_vectors = 0
    total_chunks = 0

    for batch_start in range(0, len(delete_ids), BATCH_SIZE):
        batch = delete_ids[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(delete_ids) + BATCH_SIZE - 1) // BATCH_SIZE

        try:
            # 4a. 删除 vectors（通过 document_chunks 关联）
            result = db.execute(text("""
                DELETE FROM vectors
                WHERE chunk_id IN (
                    SELECT id FROM document_chunks
                    WHERE document_id = ANY(:doc_ids)
                )
            """), {"doc_ids": batch})
            vec_del = result.rowcount
            total_vectors += vec_del

            # 4b. 删除 document_chunks
            result = db.execute(text("""
                DELETE FROM document_chunks
                WHERE document_id = ANY(:doc_ids)
            """), {"doc_ids": batch})
            chunk_del = result.rowcount
            total_chunks += chunk_del

            # 4c. 删除文档
            result = db.execute(text("""
                DELETE FROM documents
                WHERE id = ANY(:doc_ids)
            """), {"doc_ids": batch})
            doc_del = result.rowcount
            total_deleted += doc_del

            db.commit()

            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f"  批次 {batch_num}/{total_batches}: "
                      f"删除 {doc_del} 文档, {chunk_del} 分段, {vec_del} 向量 "
                      f"(累计: {total_deleted} 文档)")

        except Exception as e:
            db.rollback()
            print(f"  ✗ 批次 {batch_num} 失败: {e}")

    # ── 5. 验证结果 ──
    db.commit()

    new_total = db.execute(text("SELECT COUNT(*) FROM documents")).scalar()
    new_unique = db.execute(text(
        "SELECT COUNT(DISTINCT original_filename) FROM documents"
    )).scalar()

    print(f"\n{'=' * 60}")
    print(f"清理完成")
    print(f"  删除文档: {total_deleted}")
    print(f"  删除分段: {total_chunks}")
    print(f"  删除向量: {total_vectors}")
    print(f"  清理前: {total} 文档")
    print(f"  清理后: {new_total} 文档 (唯一: {new_unique})")
    print(f"{'=' * 60}")

    db.close()


if __name__ == "__main__":
    main()
