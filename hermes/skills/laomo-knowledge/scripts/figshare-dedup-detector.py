#!/usr/bin/env python3
"""
Figshare DUP 鉴别器 — R16 老莫沉淀 (2026-08-10)

Usage:
    # 在 cron 检索脚本最后调用，自动跳过 DUP
    dedup = FigshareDedupDetector()
    if dedup.is_figshare_dup(work, candidate_main_papers):
        print(f"[SKIP-DUP] Figshare 数据集镜像: {work.get('doi')}")
        continue

Background: Figshare DOI (10.6084/m9.figshare.*) often = a 主期刊论文的配套数据集.
直接入库会污染 known_dois.txt + 浪费 Crossref 验证配额.

强信号 (任一命中 DUP 候选):
  1. OpenAlex `type == "other"` (数据集/代码, 非 journal-article)
  2. 作者列表与 candidate_main_papers 中任一篇 完全一致 (前 5 显示名比对)

判定: 2 个强信号都命中 → is_dup = True → 跳过

Refs:
  - laomo-knowledge SKILL.md §3.1.3
"""
import urllib.request, json, urllib.error
from typing import List, Dict, Any, Set

UA = "mailto:research@yuxintech.com"


class FigshareDedupDetector:
    """Figshare DOI DUP 检测器 — 复用 OpenAlex work dict"""

    FIGSHARE_DOI_PREFIX = "10.6084/m9.figshare"

    @staticmethod
    def is_figshare_doi(doi: str) -> bool:
        if not doi:
            return False
        clean = doi.replace("https://doi.org/", "").strip()
        return clean.startswith(FigshareDedupDetector.FIGSHARE_DOI_PREFIX)

    @staticmethod
    def fetch_openalex_by_doi(doi: str, timeout: int = 15) -> Dict[str, Any]:
        """OpenAlex by DOI 反查 — 返回 work dict"""
        clean = doi.replace("https://doi.org/", "").strip()
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(clean)}"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read())

    @staticmethod
    def _author_names(work: Dict[str, Any], top_n: int = 5) -> List[str]:
        """提取前 N 个作者的 display_name"""
        out = []
        for a in work.get("authorships", [])[:top_n]:
            name = a.get("author", {}).get("display_name", "?")
            if name and name != "?":
                out.append(name)
        return out

    @staticmethod
    def _normalize_name(name: str) -> str:
        """归一化: 去空格 + 去标点 + 转小写 — 用于作者匹配"""
        return "".join(c.lower() for c in name if c.isalnum() or c.isspace()).strip()

    def _authors_match(self, figshare_authors: List[str], main_authors: List[str]) -> bool:
        """前 5 作者完全一致 — Figshare DUP 最强信号"""
        if not figshare_authors or not main_authors:
            return False
        norm_fig = [self._normalize_name(a) for a in figshare_authors[:5]]
        norm_main = [self._normalize_name(a) for a in main_authors[:5]]
        return norm_fig == norm_main

    def is_figshare_dup(
        self,
        figshare_doi: str,
        candidate_main_papers: List[Dict[str, Any]],
        fetch_if_needed: bool = True,
    ) -> bool:
        """
        判定 Figshare DOI 是否为 DUP 数据镜像.

        Args:
            figshare_doi: 待检测的 Figshare DOI
            candidate_main_papers: 已收录的候选主论文列表 (OpenAlex work dict 数组)
                                   也可传作者列表字符串数组: ["Xie, Xiao", "Zhang, Bo", ...]
            fetch_if_needed: True 则自动 OpenAlex 反查 (默认); False 则跳过反查

        Returns:
            True = DUP 跳过; False = 独立论文继续评估
        """
        if not self.is_figshare_doi(figshare_doi):
            return False  # 非 Figshare DOI 不归本检测器管

        # 1. 拿 Figshare work dict (OpenAlex 反查)
        try:
            fs_work = self.fetch_openalex_by_doi(figshare_doi) if fetch_if_needed else None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Crossref 反查已确认 404, OpenAlex 也没收录 — 仍按 DUP 处理
                return True
            raise

        if not fs_work:
            return False

        # 强信号 1: type == "other"
        work_type = fs_work.get("type", "")
        is_other_type = work_type == "other"

        # 强信号 2: 作者列表与主论文完全一致
        fs_authors = self._author_names(fs_work)
        author_match_found = False
        for main_paper in candidate_main_papers or []:
            if isinstance(main_paper, dict):
                main_authors = self._author_names(main_paper)
            else:
                # 兼容字符串列表
                main_authors = list(main_paper) if main_paper else []
            if self._authors_match(fs_authors, main_authors):
                author_match_found = True
                break

        # 判定: 2 强信号全中 → DUP
        return is_other_type and author_match_found


# CLI 演示 (老莫 cron 脚本可 import 复用)
if __name__ == "__main__":
    import sys

    print("Figshare DUP 鉴别器 v1 (R16)")
    print(f"判定规则: type=other AND 作者列表完全一致 → DUP 跳过")
    print(f"详细文档见 laomo-knowledge SKILL.md §3.1.3")

    # 示例: 检测一个 DOI
    if len(sys.argv) > 1:
        test_doi = sys.argv[1]
        detector = FigshareDedupDetector()
        if detector.is_figshare_doi(test_doi):
            print(f"\n测试 DOI: {test_doi}")
            print(f"是 Figshare DOI, 自动判定...")
            try:
                work = detector.fetch_openalex_by_doi(test_doi)
                print(f"  title: {work.get('title')}")
                print(f"  type: {work.get('type')}")
                print(f"  authors: {detector._author_names(work)}")
                print(f"  -> 如未传 candidate_main_papers, 仅展示信息 (传了再 DUP 判定)")
            except Exception as e:
                print(f"  fetch error: {e}")
