# -*- coding: utf-8 -*-
"""
schemas.py — Pydantic data models for the aquaculture-water-quality-optimizer harness.

These models enforce type safety, range validation, and canonical structure across
intake, framework selection, scoring, and roadmap generation. They are used by the
sub-skill markdown prompts and by the Python scoring/roadmap engines.
"""
from __future__ import annotations

import math
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class SystemType(str, Enum):
    POND = "pond"
    RAS = "ras"
    BIOFLOC = "biofloc"
    FLOW_THROUGH = "flow-through"
    CAGE = "cage"
    RECIRCULATING_AQUACULTURE = "ras"


class LifeStage(str, Enum):
    LARVAE = "larvae"
    JUVENILE = "juvenile"
    ADULT = "adult"
    BROODSTOCK = "broodstock"
    MIXED = "mixed"


class WaterParameters(BaseModel):
    """Measured water-chemistry and physical parameters."""

    do_mg_l: Optional[float] = Field(None, ge=0.0, le=25.0, description="Dissolved oxygen in mg/L")
    tan_mg_l: Optional[float] = Field(None, ge=0.0, description="Total ammonia nitrogen in mg/L")
    no2_mg_l: Optional[float] = Field(None, ge=0.0, description="Nitrite in mg/L")
    no3_mg_l: Optional[float] = Field(None, ge=0.0, description="Nitrate in mg/L")
    ph: Optional[float] = Field(None, ge=0.0, le=14.0, description="pH")
    alkalinity_mg_l_caCO3: Optional[float] = Field(None, ge=0.0, description="Alkalinity as mg/L CaCO3")
    temp_c: Optional[float] = Field(None, ge=-2.0, le=45.0, description="Water temperature in °C")
    salinity_ppt: Optional[float] = Field(None, ge=0.0, le=50.0, description="Salinity in ppt")
    turbidity_ntu: Optional[float] = Field(None, ge=0.0, description="Turbidity in NTU")
    c_n_ratio: Optional[float] = Field(None, ge=0.0, description="Carbon:Nitrogen ratio for biofloc")
    tss_mg_l: Optional[float] = Field(None, ge=0.0, description="Total suspended solids in mg/L")
    secchi_cm: Optional[float] = Field(None, ge=0.0, description="Secchi disk depth in cm")

    @model_validator(mode="after")
    def check_temperature_salinity_ph_present(self):
        # NH3 and many envelope calculations require these three; missing is OK but lowers confidence.
        return self

    @property
    def unionized_nh3_mg_l(self) -> Optional[float]:
        """
        Un-ionized ammonia (NH3-N) concentration using the Emerson et al. (1975)
        aqueous ammonia equilibrium relationship.
        Source: Emerson K, Russo RC, Lund RE, Thurston RV (1975) J Fish Res Board Can 32:2379-2383.
        """
        if self.tan_mg_l is None or self.ph is None or self.temp_c is None:
            return None
        if self.tan_mg_l <= 0 or self.ph <= 0:
            return 0.0
        tk = self.temp_c + 273.15
        # pKa = 0.09018 + 2729.92 / T(K)
        pka = 0.09018 + (2729.92 / tk)
        fraction_nh3 = 1.0 / (10.0 ** (pka - self.ph) + 1.0)
        return self.tan_mg_l * fraction_nh3

    @property
    def percent_saturation(self) -> Optional[float]:
        """
        Approximate DO percent saturation at 1 atm, fresh to brackish water.
        Uses the polynomial of Weiss (1970; Limnology & Oceanography) for seawater,
        salinity-corrected.
        """
        if self.do_mg_l is None or self.temp_c is None or self.salinity_ppt is None:
            return None
        T = self.temp_c + 273.15
        S = self.salinity_ppt
        lnCs = (
            -173.4292
            + 249.6339 * (100 / T)
            + 143.3483 * math.log(T / 100)
            - 21.8492 * (T / 100)
            + S * (-0.033096 + 0.014259 * (T / 100) - 0.0017 * (T / 100) ** 2)
        )
        saturation_mg_l = math.exp(lnCs) * 1.42905  # convert mL/L to mg/L
        if saturation_mg_l <= 0:
            return None
        return round((self.do_mg_l / saturation_mg_l) * 100.0, 1)


class StockingInfo(BaseModel):
    species: str = Field(..., min_length=1, description="Species common or scientific name")
    scientific_name: Optional[str] = Field(None, description="Scientific name if known")
    system_type: SystemType = Field(..., description="Production system type")
    life_stage: LifeStage = LifeStage.MIXED
    stocking_density_kg_m3: Optional[float] = Field(None, ge=0.0, description="Biomass density kg/m³")
    stocking_count_m2: Optional[float] = Field(None, ge=0.0, description="Animals per m² (ponds) or m³ (RAS)")
    water_volume_m3: Optional[float] = Field(None, ge=0.0, description="System water volume in m³")
    production_target_kg: Optional[float] = Field(None, ge=0.0, description="Harvest target kg")
    feed_rate_kg_day: Optional[float] = Field(None, ge=0.0, description="Daily feed input kg/day")
    culture_days: Optional[int] = Field(None, ge=0, description="Days since stocking")


class BiosecurityFlags(BaseModel):
    recent_mortality: bool = False
    recent_stocking_without_quarantine: bool = False
    shared_equipment_between_ponds: bool = False
    predators_or_birds_observed: bool = False
    untreated_water_source: bool = False
    recent_weather_extreme: bool = False
    disease_history: bool = False
    health_checks_documented: bool = False
    veterinary_oversight: bool = False


class IntakeProfile(BaseModel):
    """Canonical output of sub-profile-intake."""

    farm_id: Optional[str] = None
    location: Optional[str] = None
    intake_date: Optional[date] = None
    stocking: StockingInfo
    water: WaterParameters
    biosecurity: BiosecurityFlags = Field(default_factory=BiosecurityFlags)
    notes: Optional[str] = None
    missing_fields: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    confidence: str = Field("medium", pattern="^(low|medium|high)$")

    @property
    def critical_missing(self) -> List[str]:
        required = ["stocking.species", "stocking.system_type"]
        if self.stocking.system_type in (SystemType.POND, SystemType.BIOFLOC):
            required.append("water.ph")
            required.append("water.temp_c")
        else:
            required.extend(["water.do_mg_l", "water.temp_c", "water.ph"])
        present = {
            "stocking.species": bool(self.stocking.species),
            "stocking.system_type": bool(self.stocking.system_type),
            "water.do_mg_l": self.water.do_mg_l is not None,
            "water.temp_c": self.water.temp_c is not None,
            "water.ph": self.water.ph is not None,
        }
        return [f for f in required if not present.get(f, False)]


class EnvelopeCriterion(BaseModel):
    """A single water-quality envelope boundary for one parameter."""

    parameter: str
    unit: str
    min_optimal: Optional[float] = None
    max_optimal: Optional[float] = None
    min_stress: Optional[float] = None
    max_stress: Optional[float] = None
    lethal_below: Optional[float] = None
    lethal_above: Optional[float] = None
    source: str
    applies_to: Optional[str] = None  # e.g. "pond", "ras", "biofloc"


class Framework(BaseModel):
    """Named, citable evaluation framework returned by sub-framework-selector."""

    name: str
    species: List[str]
    system_types: List[SystemType]
    life_stages: List[LifeStage]
    envelope: List[EnvelopeCriterion]
    carrying_capacity_model: Optional[str] = None
    biosecurity_standard: Optional[str] = None
    citations: List[str] = Field(default_factory=list)
    rationale: str


class DimensionScore(BaseModel):
    dimension: str = Field(..., pattern="^(Oxygen status|Nitrogen toxicity risk|pH/alkalinity stability|Temperature/salinity fit|Biosecurity)$")
    value: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    justification: str
    sources: List[str]
    flagged_params: List[str] = Field(default_factory=list)
    confidence: str = Field("medium", pattern="^(low|medium|high)$")


class CompositeScore(BaseModel):
    dimensions: List[DimensionScore]
    composite: float = Field(..., ge=0.0, le=100.0)
    confidence: str
    missing_data_note: Optional[str] = None

    @property
    def top_risk_dimension(self) -> Optional[DimensionScore]:
        if not self.dimensions:
            return None
        return min(self.dimensions, key=lambda d: d.value)

    def dimension_score(self, name: str) -> float:
        return next((d.value for d in self.dimensions if d.dimension == name), 70.0)


class RoadmapItem(BaseModel):
    rank: int = Field(..., ge=1)
    action: str
    target_parameter: Optional[str] = None
    target_dimension: Optional[str] = None
    effort: str = Field(..., pattern="^(low|medium|high)$")
    impact: str = Field(..., pattern="^(low|medium|high)$")
    rationale: str
    owner: str
    expected_effect: str
    framework_source: str
    urgency_hours: Optional[float] = None


class Roadmap(BaseModel):
    items: List[RoadmapItem]
    monitoring_schedule: Optional[str] = None
    stopgap_note: Optional[str] = None


class ImprovementArtifact(BaseModel):
    profile: IntakeProfile
    framework: Framework
    score: CompositeScore
    roadmap: Roadmap
    assumptions: List[str]
    limitations: List[str]
    sources: List[str]


class KnowledgeEntry(BaseModel):
    """Canonical entry appended to SECOND-KNOWLEDGE-BRAIN.md by the knowledge updater."""

    title: str
    authors: str
    year: int = Field(..., ge=1900, le=2100)
    venue: str
    url: Optional[str] = None
    doi: Optional[str] = None
    abstract: str = ""
    key_findings: str = ""
    relevance: str = ""
    source_api: str
    queried_date: date = Field(default_factory=date.today)

