"""
本地文档中转站扫描任务 — 定时扫描本地文件夹，自动导入RKR处理管道

v7: 修复重复导入问题
- 去重覆盖所有状态（含failed → 重置重试，不复建新记录）
- 增加 staging_id 批次去重（external_agent_metadata.staging_id）
- 增加 SHA256 内容哈希去重
- 增加单轮导入上限保护

用法：
- celery beat 每30秒调度一次
- 扫描 LOCAL_STAGING_DIR 目录下的文档文件
- 新文件 → 复制到 文档库/{项目名}/ → 触发 process_shared_document
- 处理完成后删除中转站原始文件（自动清零）
"""
import os
import uuid
import logging
import hashlib
import shutil
from datetime import datetime
from sqlalchemy import select, or_

from app.celery_app import celery_app
from app.core.database import sync_session_maker
from app.models.document import Document

logger = logging.getLogger(__name__)

# 中转站路径
def _get_staging_dir():
    from app.services.staging_config import get_staging_dir
    return get_staging_dir()

# 文档库根目录（RKR 项目下的 文档库/）
DOC_LIBRARY_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "文档库")

# 中转站项目ID
STAGING_PROJECT_ID = uuid.UUID("***SECRET***")
# 系统用户ID
SYSTEM_USER_ID = uuid.UUID("***SECRET***")

# v7: 单轮导入上限（防止管道积压时无限导入）
MAX_IMPORT_PER_SCAN = 50

EXT_MIME_MAP = {
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".csv": "text/csv",
    ".xml": "text/xml",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".ppt": "application/vnd.ms-powerpoint",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
}


def _compute_content_hash(filepath: str, sample_size: int = 8192) -> str:
    """计算文件内容哈希（取前8KB + 文件大小作为指纹）"""
    try:
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            # 读取文件头用于快速指纹
            sha.update(f.read(sample_size))
        # 加入文件大小增强唯一性
        file_size = os.path.getsize(filepath)
        sha.update(str(file_size).encode())
        return sha.hexdigest()
    except Exception:
        return ""


def _resolve_project_name(project_id: uuid.UUID) -> str:
    """根据项目ID查项目名，返回安全的目录名"""
    db = sync_session_maker()
    try:
        from app.models.project import Project
        proj = db.get(Project, project_id)
        if proj and proj.name:
            return proj.name.replace("/", "_").replace("\\", "_").strip()
        return None
    except Exception:
        return None
    finally:
        db.close()


def _build_doc_library_path(project_name: str, filename: str) -> str:
    """构建文档库中的完整路径: 文档库/{项目名}/{文件名}"""
    safe_name = project_name.replace("/", "_").replace("\\", "_").strip()
    proj_dir = os.path.join(DOC_LIBRARY_ROOT, safe_name)
    os.makedirs(proj_dir, exist_ok=True)

    # 处理重名：追加序号
    dest_path = os.path.join(proj_dir, filename)
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(proj_dir, f"{base}_{counter}{ext}")):
            counter += 1
        dest_path = os.path.join(proj_dir, f"{base}_{counter}{ext}")

    return dest_path


def _check_staging_id_duplicate(db, staging_id: str) -> bool:
    """检查同一个 staging_id 批次是否已经导入过

    如果已有任何文档携带相同的 staging_id，返回 True
    """
    if not staging_id:
        return False
    try:
        existing = db.execute(
            select(Document.id).where(
                Document.external_agent_metadata.contains(staging_id)
            ).limit(1)
        ).scalar_one_or_none()
        return existing is not None
    except Exception:
        return False


def _check_content_hash_duplicate(db, content_hash: str) -> uuid.UUID | None:
    """检查相同内容哈希的文档是否已存在

    返回已存在的文档ID，如果不存在返回 None
    """
    if not content_hash:
        return None
    try:
        # 在 external_agent_metadata JSON 字段中查找 content_hash
        existing = db.execute(
            select(Document.id).where(
                Document.external_agent_metadata.contains(content_hash)
            ).limit(1)
        ).scalar_one_or_none()
        return existing
    except Exception:
        return None


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def scan_local_staging(self):
    """扫描本地中转站，导入新文档（v7：增强去重）"""
    staging_dir = _get_staging_dir()
    if not os.path.isdir(staging_dir):
        logger.warning(f"[LocalStaging] 目录不存在: {staging_dir}")
        return {"status": "skipped", "reason": "directory not found"}

    db = sync_session_maker()
    imported = 0
    errors = 0
    skipped_dup = 0
    skipped_staging_id = 0
    retried_failed = 0

    try:
        from app.models.user import User  # noqa
        from app.models.project import Project  # noqa
        from app.models.knowledge_category import KnowledgeCategory  # noqa

        all_files = sorted([f for f in os.listdir(staging_dir)
                           if not os.path.isdir(os.path.join(staging_dir, f))
                           and not f.startswith(".")
                           and "_log" not in f
                           and os.path.splitext(f)[1].lower() in EXT_MIME_MAP])
        batch = all_files[:MAX_IMPORT_PER_SCAN]
        imported = 0
        errors = 0
        skipped_dup = 0
        skipped_staging_id = 0
        retried_failed = 0

        # v7: 跟踪本轮已处理的 staging_id（避免同批次多个文件重复检查）
        seen_staging_ids = set()

        for filename in batch:
            filepath = os.path.join(staging_dir, filename)
            ext = os.path.splitext(filename)[1].lower()

            try:
                file_size = os.path.getsize(filepath)

                # ── 读取元数据侧车（外部Agent写入的 .meta.json）──
                meta_path = filepath + ".meta.json"
                meta = {}
                if os.path.exists(meta_path):
                    try:
                        import json as _json
                        with open(meta_path, "r", encoding="utf-8") as mf:
                            meta = _json.load(mf)
                    except Exception:
                        pass

                # ── v7: staging_id 批次去重 ──
                ext_meta = meta.get("external_agent_metadata")
                if isinstance(ext_meta, str):
                    try:
                        ext_meta = _json.loads(ext_meta) if ext_meta else {}
                    except Exception:
                        ext_meta = {}
                elif ext_meta is None:
                    ext_meta = {}

                staging_id = ext_meta.get("staging_id") if isinstance(ext_meta, dict) else None
                if staging_id:
                    if staging_id in seen_staging_ids:
                        # 同批次已处理过 → 删除文件
                        logger.info(f"[LocalStaging] 批次去重(本轮): {filename} staging_id={staging_id}")
                        os.remove(filepath)
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        skipped_staging_id += 1
                        continue
                    if _check_staging_id_duplicate(db, staging_id):
                        # 历史批次已存在 → 删除文件
                        logger.info(f"[LocalStaging] 批次去重(历史): {filename} staging_id={staging_id}")
                        os.remove(filepath)
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        skipped_staging_id += 1
                        seen_staging_ids.add(staging_id)
                        continue
                    seen_staging_ids.add(staging_id)

                # ── v7: 内容哈希去重 ──
                content_hash = _compute_content_hash(filepath)
                if content_hash:
                    ext_meta["content_hash"] = content_hash  # 存入 metadata 供后续查重
                    hash_existing = _check_content_hash_duplicate(db, content_hash)
                    if hash_existing:
                        logger.info(f"[LocalStaging] 内容哈希去重: {filename} (已存在: {hash_existing})")
                        os.remove(filepath)
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        skipped_dup += 1
                        continue

                # 解析项目ID
                project_id_str = meta.get("project_id")
                if project_id_str:
                    try:
                        doc_project_id = uuid.UUID(project_id_str)
                    except (ValueError, TypeError):
                        doc_project_id = STAGING_PROJECT_ID
                else:
                    doc_project_id = STAGING_PROJECT_ID

                mime_type = EXT_MIME_MAP[ext]

                # 解析上传者ID
                uploaded_by_str = meta.get("uploaded_by")
                if uploaded_by_str:
                    try:
                        uploaded_by = uuid.UUID(uploaded_by_str)
                    except (ValueError, TypeError):
                        uploaded_by = SYSTEM_USER_ID
                else:
                    uploaded_by = SYSTEM_USER_ID

                dest_filename = meta.get("original_filename") or filename

                # ── v7: 增强去重检查（覆盖所有状态）──
                existing = db.execute(
                    select(Document).where(
                        Document.original_filename == dest_filename,
                        Document.file_size == file_size,
                    ).limit(1)
                ).scalar_one_or_none()

                if existing:
                    status = existing.processing_status
                    if status == "completed":
                        # 已成功处理 → 跳过
                        logger.info(f"[LocalStaging] 去重跳过(completed): {filename} → {existing.id}")
                        os.remove(filepath)
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        skipped_dup += 1
                        continue
                    elif status == "uploaded":
                        # 正在排队处理 → 跳过
                        logger.info(f"[LocalStaging] 去重跳过(uploaded): {filename} → {existing.id}")
                        os.remove(filepath)
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        skipped_dup += 1
                        continue
                    elif status == "failed":
                        # v7 关键修复：文档曾经失败 → 重置状态，重新触发处理，不新建记录！
                        logger.info(f"[LocalStaging] 重试失败文档: {filename} → {existing.id}")
                        existing.processing_status = "uploaded"
                        existing.error_message = ""
                        existing.chunk_count = 0
                        existing.updated_at = datetime.utcnow()
                        # 更新 metadata（可能有新的 tags/source 等信息）
                        if meta.get("tags"):
                            existing.tags = meta.get("tags")
                        if ext_meta:
                            existing.external_agent_metadata = ext_meta
                        db.flush()

                        from app.tasks.document_processing import process_shared_document
                        process_shared_document.delay(document_id=str(existing.id))

                        # 删除中转站文件
                        os.remove(filepath)
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        log_file = os.path.join(staging_dir, f"{os.path.splitext(filename)[0]}_log.json")
                        if os.path.exists(log_file):
                            os.remove(log_file)
                        retried_failed += 1
                        continue
                    else:
                        # 未知状态，保守跳过
                        logger.warning(f"[LocalStaging] 未知状态跳过: {filename} status={status}")
                        skipped_dup += 1
                        continue

                # ── 新文档：正常导入 ──
                proj_name = _resolve_project_name(doc_project_id)
                if not proj_name:
                    proj_name = "未分类"
                doc_library_path = _build_doc_library_path(proj_name, dest_filename)

                shutil.copy2(filepath, doc_library_path)
                logger.info(f"[LocalStaging] 文档入库: {filename} → 文档库/{proj_name}/{os.path.basename(doc_library_path)}")

                doc = Document(
                    id=uuid.uuid4(),
                    project_id=doc_project_id,
                    file_path=doc_library_path,
                    original_filename=dest_filename,
                    uploaded_by=uploaded_by,
                    file_size=file_size,
                    mime_type=meta.get("mime_type") or mime_type,
                    processing_status="uploaded",
                    chunk_count=0,
                    error_message="",
                    source=meta.get("source") or "local_staging",
                    source_url=meta.get("source_url") or f"file://{filepath}",
                    tags=meta.get("tags") or [],
                    external_agent_metadata=ext_meta if ext_meta else None,
                )
                cat_id_str = meta.get("category_id")
                if cat_id_str:
                    try:
                        doc.category_id = uuid.UUID(cat_id_str)
                    except (ValueError, TypeError):
                        pass

                db.add(doc)
                db.flush()

                from app.tasks.document_processing import process_shared_document
                process_shared_document.delay(document_id=str(doc.id))

                os.remove(filepath)
                if os.path.exists(meta_path):
                    os.remove(meta_path)
                log_file = os.path.join(staging_dir, f"{os.path.splitext(filename)[0]}_log.json")
                if os.path.exists(log_file):
                    os.remove(log_file)

                imported += 1
                logger.info(f"[LocalStaging] 已导入: {filename} → {doc.id}")

            except Exception as e:
                errors += 1
                logger.error(f"[LocalStaging] 导入失败 {filename}: {e}")

        db.commit()

        result = {
            "status": "success" if (imported > 0 or retried_failed > 0) else "idle",
            "imported": imported,
            "retried_failed": retried_failed,
            "skipped_duplicate": skipped_dup,
            "skipped_staging_id": skipped_staging_id,
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
        }
        logger.info(f"[LocalStaging] v7 扫描完成: {result}")
        return result

    except Exception as e:
        db.rollback()
        logger.error(f"[LocalStaging] 扫描异常: {e}")
        raise self.retry(exc=e)
    finally:
        db.close()
