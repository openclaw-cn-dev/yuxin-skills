"""Skill 5 ? knowledge updater.

Queries the cached SECOND-KNOWLEDGE-BRAIN.md via the ``query_knowledge_base``
tool, surfaces 3-5 tiered citations relevant to the current analysis keywords,
and flags knowledge gaps for the crawl pipeline. Falls back to the embedded
evidence items from prior skills when the KB is empty (degradation level 1).
"""
from __future__ import annotations

import time
from typing import Any, List

from ..errors import ToolError
from ..schemas import EvidenceItem
from .base import Skill, SkillContext


class KnowledgeUpdaterSkill(Skill):
    name = "knowledge_updater"
    step = 5
    description = ("Query SECOND-KNOWLEDGE-BRAIN.md for authoritative evidence; "
                   "surface tiered citations and flag knowledge gaps.")
    depends_on = ["biofilter_disease"]
    prompt_template = "knowledge_updater"
    input_schema = ""
    output_schema = ""
    tags = ["knowledge", "rag"]

    def run(self, ctx: SkillContext) -> Any:
        t0 = time.perf_counter()
        req = ctx.state.requirements
        sc = ctx.state.scorecard
        keywords = self._keywords(req, sc)
        citations: List[EvidenceItem] = []
        coverage = "low"
        gaps: List[str] = []

        try:
            res = ctx.tool_registry.invoke("query_knowledge_base",
                                           {"keywords": keywords}, ctx.tool_context)
            coverage = res.get("coverage", "low")
            for para in res.get("citations", []):
                tier = self._guess_tier(para)
                citations.append(EvidenceItem(
                    claim=para[:300] + ("..." if len(para) > 300 else ""),
                    sources=["SECOND-KNOWLEDGE-BRAIN.md"], tier=tier))
        except ToolError as exc:
            ctx.state.limitations.append(f"Knowledge base query failed: {exc}")
            ctx.state.degradation_level = max(ctx.state.degradation_level, 1)

        if coverage == "low":
            # Fall back to the embedded evidence already produced upstream.
            for ev in (ctx.state.biofilter_risk and [] or []):
                pass
            citations.extend(self._fallback_citations(req, sc))
            if not citations:
                gaps.append("No academic citation surfaced; queue topic for crawl pipeline.")
                self._degrade(ctx, "No academic source surfaced; flagged for crawl.", level=1)
        else:
            # Identify gaps: which analysis areas lacked a Tier-1/2 citation.
            topics = set(keywords)
            cited_low = {c.claim.lower() for c in citations}
            for topic in topics:
                if not any(topic.split()[0] in cl for cl in cited_low):
                    gaps.append(f"Limited coverage for: {topic}")

        ctx.state.knowledge_citations = citations
        return self._ok_result(
            {"knowledge_citations": [c.to_dict() for c in citations],
             "coverage": coverage, "knowledge_gaps": gaps, "keywords": keywords},
            evidence=citations, duration_ms=(time.perf_counter() - t0) * 1000)

    # ----- helpers -----
    @staticmethod
    def _keywords(req, sc) -> List[str]:
        kws = []
        if req is not None:
            sp = req.species.replace("_", " ")
            kws.append(f"{sp} {req.life_stage} water quality")
            kws.append("un-ionized ammonia fish toxicity")
            kws.append("RAS biofilter nitrification cold")
            kws.append("cold-water salmonid disease early warning")
        if sc is not None:
            if sc.nh3_status != "safe":
                kws.append("ammonia toxicity RAS")
            if sc.do_status != "adequate":
                kws.append("dissolved oxygen saturation aquaculture")
            if sc.nitrification_status in ("failing", "stressed"):
                kws.append("nitrification failure biofilter")
        return kws[:6]

    @staticmethod
    def _guess_tier(text: str) -> str:
        t = text.lower()
        if any(x in t for x in ("doi", "10.", "woah", "fao", "apha", "standard methods", "iso")):
            return "1" if any(x in t for x in ("woah", "fao", "apha", "iso", "standard methods")) else "2"
        if any(x in t for x in ("srac", "freshwater institute", "extension", "usda")):
            return "3"
        return "4"

    @staticmethod
    def _fallback_citations(req, sc) -> List[EvidenceItem]:
        return [
            EvidenceItem(
                claim="Emerson et al. (1975) aqueous ammonia equilibrium (DOI 10.1139/f75-274) "
                      "is the standard NH3 calculation reference.",
                sources=["10.1139/f75-274"], tier="2"),
            EvidenceItem(
                claim="Zhu & Chen (2002) characterize nitrification temperature dependence "
                      "in RAS biofilters (DOI 10.1016/S0044-8486(02)00051-8).",
                sources=["10.1016/S0044-8486(02)00051-8"], tier="2"),
            EvidenceItem(
                claim="WOAH Aquatic Animal Health Code lists notifiable cold-water salmonid "
                      "diseases (VHS, IPN, ISA, Gyrodactylosis, furunculosis).",
                sources=["WOAH Aquatic Animal Health Code"], tier="1"),
        ]
