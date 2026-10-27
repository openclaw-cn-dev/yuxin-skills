"""ras_aqua skills package ? concrete skill executors.

Each module implements one skill as a ``Skill`` subclass with a deterministic
``run`` method that uses the real domain functions (chemistry, biofilter,
diseases, species) and the tool registry. The engine wires these into the
``SkillRegistry`` and executes them in order.
"""
from __future__ import annotations

from .base import Skill, SkillContext, SkillState
from .gather_requirements import GatherRequirementsSkill
from .evidence_collector import EvidenceCollectorSkill
from .water_quality_analysis import WaterQualityAnalysisSkill
from .biofilter_disease import BiofilterDiseaseSkill
from .knowledge_updater import KnowledgeUpdaterSkill
from .ras_advisor import RasAdvisorSkill

__all__ = [
    "Skill", "SkillContext", "SkillState",
    "GatherRequirementsSkill", "EvidenceCollectorSkill",
    "WaterQualityAnalysisSkill", "BiofilterDiseaseSkill",
    "KnowledgeUpdaterSkill", "RasAdvisorSkill",
]


def all_skills():
    """Instantiate the default skill set in execution order."""
    return [
        GatherRequirementsSkill(),
        EvidenceCollectorSkill(),
        WaterQualityAnalysisSkill(),
        BiofilterDiseaseSkill(),
        KnowledgeUpdaterSkill(),
        RasAdvisorSkill(),
    ]
