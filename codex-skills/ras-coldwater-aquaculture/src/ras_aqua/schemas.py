"""Typed data models (dataclasses + enums) for the ras_aqua engine.

These mirror the JSON schemas under ``assets/schemas/`` and are the canonical
in-process representations. Conversion helpers (``from_dict`` / ``to_dict``)
keep the boundary with the LLM/JSON layer clean and validated.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    OK = "ok"
    WATCH = "watch"
    ALERT = "alert"
    CRITICAL = "critical"


class VerdictCategory(str, Enum):
    OPTIMAL = "Optimal"
    ADJUST = "Adjust Required"
    CRITICAL = "Critical Alert"
    INCONCLUSIVE = "Inconclusive"


class Status(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    ERROR = "error"


class TargetObjective(str, Enum):
    HEALTH = "health_assessment"
    DESIGN = "design_check"
    TROUBLESHOOT = "troubleshoot_excursion"
    BIOFILTER = "biofilter_sizing"
    GENERAL = "general_advice"


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

@dataclass
class WaterQualityReading:
    T_C: float
    DO_mgL: Optional[float] = None
    pH: Optional[float] = None
    TAN_mgL: Optional[float] = None
    NO2_mgL: Optional[float] = None
    NO3_mgL: Optional[float] = None
    alkalinity_mgL: Optional[float] = None
    CO2_mgL: Optional[float] = None
    salinity_ppt: Optional[float] = 0.0
    timestamp: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WaterQualityReading":
        return cls(
            T_C=float(d["T_C"]),
            DO_mgL=_opt_float(d.get("DO_mgL")),
            pH=_opt_float(d.get("pH")),
            TAN_mgL=_opt_float(d.get("TAN_mgL")),
            NO2_mgL=_opt_float(d.get("NO2_mgL")),
            NO3_mgL=_opt_float(d.get("NO3_mgL")),
            alkalinity_mgL=_opt_float(d.get("alkalinity_mgL")),
            CO2_mgL=_opt_float(d.get("CO2_mgL")),
            salinity_ppt=_opt_float(d.get("salinity_ppt")) or 0.0,
            timestamp=d.get("timestamp"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RasConfig:
    tank_volume_m3: Optional[float] = None
    makeup_pct: Optional[float] = None
    biofilter_type: Optional[str] = None
    biofilter_media_volume_m3: Optional[float] = None
    biofilter_area_m2: Optional[float] = None
    flow_lpm: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "RasConfig":
        d = d or {}
        return cls(
            tank_volume_m3=_opt_float(d.get("tank_volume_m3")),
            makeup_pct=_opt_float(d.get("makeup_pct")),
            biofilter_type=d.get("biofilter_type"),
            biofilter_media_volume_m3=_opt_float(d.get("biofilter_media_volume_m3")),
            biofilter_area_m2=_opt_float(d.get("biofilter_area_m2")),
            flow_lpm=_opt_float(d.get("flow_lpm")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Requirements:
    species: str
    life_stage: str
    wq: WaterQualityReading
    target_objective: TargetObjective = TargetObjective.GENERAL
    language: str = "en"
    ras_config: RasConfig = field(default_factory=RasConfig)
    biomass_kg: Optional[float] = None
    feed_kg_day: Optional[float] = None
    feed_protein_pct: Optional[float] = None
    species_common_name: Optional[str] = None
    notes: Optional[str] = None
    clarifying_questions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Requirements":
        wq = WaterQualityReading.from_dict(d["wq"])
        obj = d.get("target_objective", "general_advice")
        try:
            objective = TargetObjective(obj)
        except ValueError:
            objective = TargetObjective.GENERAL
        return cls(
            species=d["species"],
            life_stage=d["life_stage"],
            wq=wq,
            target_objective=objective,
            language=d.get("language", "en"),
            ras_config=RasConfig.from_dict(d.get("ras_config")),
            biomass_kg=_opt_float(d.get("biomass_kg")),
            feed_kg_day=_opt_float(d.get("feed_kg_day")),
            feed_protein_pct=_opt_float(d.get("feed_protein_pct")),
            species_common_name=d.get("species_common_name"),
            notes=d.get("notes"),
            clarifying_questions=list(d.get("clarifying_questions", []) or []),
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["target_objective"] = self.target_objective.value
        return d


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

@dataclass
class Deviation:
    parameter: str
    value: Optional[float]
    envelope: str
    severity: Severity = Severity.OK
    delta: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class WaterQualityScorecard:
    nh3_mgL: Optional[float]
    nh3_fraction: Optional[float]
    nh3_status: str
    do_sat_pct: Optional[float]
    do_status: str
    nitrification_status: str
    alkalinity_status: str
    alkalinity_demand_mgL_CaCO3_per_day: Optional[float]
    co2_status: str
    deviations: List[Deviation] = field(default_factory=list)
    trend: Optional[str] = None
    data_quality_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["deviations"] = [dv.to_dict() for dv in self.deviations]
        return d


@dataclass
class DiseaseWarning:
    disease: str
    signal: str
    matched_conditions: List[str]
    severity: Severity
    woah_notifiable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class Treatment:
    action: str
    rationale: str
    magnitude: str
    category: str = "operational"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BiofilterRisk:
    biofilter_capacity_status: str
    disease_early_warning: List[DiseaseWarning] = field(default_factory=list)
    recommended_treatments: List[Treatment] = field(default_factory=list)
    tan_production_g_day: Optional[float] = None
    biofilter_capacity_g_day: Optional[float] = None
    loading_ratio: Optional[float] = None
    nitrification_penalty_pct: Optional[float] = None
    advanced_biofiltration_options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["disease_early_warning"] = [w.to_dict() for w in self.disease_early_warning]
        d["recommended_treatments"] = [t.to_dict() for t in self.recommended_treatments]
        return d


@dataclass
class EvidenceItem:
    claim: str
    sources: List[str] = field(default_factory=list)
    tier: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TreatmentStep:
    step: int
    action: str
    magnitude: str = ""
    safety_limit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Verdict:
    verdict: VerdictCategory
    disclosure: str
    early_warning_alerts: List[str]
    water_treatment_procedure: List[TreatmentStep]
    key_risks: List[str] = field(default_factory=list)
    evidence_chain: List[EvidenceItem] = field(default_factory=list)
    remediation: List[str] = field(default_factory=list)
    scenarios: Dict[str, str] = field(default_factory=dict)
    degradation_level: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        d["evidence_chain"] = [e.to_dict() for e in self.evidence_chain]
        d["water_treatment_procedure"] = [s.to_dict() for s in self.water_treatment_procedure]
        return d


@dataclass
class SkillResult:
    """Generic envelope returned by every skill execution."""
    skill: str
    status: Status
    data: Dict[str, Any]
    limitations: List[str] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)
    degradation_level: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "skill": self.skill,
            "status": self.status.value,
            "data": self.data,
            "limitations": self.limitations,
            "evidence": [e.to_dict() for e in self.evidence],
            "degradation_level": self.degradation_level,
            "duration_ms": round(self.duration_ms, 2),
        }
        return d


@dataclass
class EngineReport:
    requirements: Requirements
    scorecard: Optional[WaterQualityScorecard]
    biofilter_risk: Optional[BiofilterRisk]
    verdict: Optional[Verdict]
    knowledge_citations: List[EvidenceItem]
    quality_gate_results: Dict[str, str]
    degradation_level: int
    limitations: List[str]
    language: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirements": self.requirements.to_dict(),
            "scorecard": self.scorecard.to_dict() if self.scorecard else None,
            "biofilter_risk": self.biofilter_risk.to_dict() if self.biofilter_risk else None,
            "verdict": self.verdict.to_dict() if self.verdict else None,
            "knowledge_citations": [e.to_dict() for e in self.knowledge_citations],
            "quality_gate_results": self.quality_gate_results,
            "degradation_level": self.degradation_level,
            "limitations": self.limitations,
            "language": self.language,
        }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _opt_float(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
