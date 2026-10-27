# -*- coding: utf-8 -*-
"""
frameworks.py — Named, citable water-quality envelopes and management frameworks.

Every envelope bound here is traceable to a named source in aquaculture science:
- Boyd & Tucker (1998) Pond Aquaculture Water Quality Management
- Boyd (2020) Water Quality: An Introduction
- Timmons & Guerdat (2017) Recirculating Aquaculture
- Avnimelech (2012) Biofloc Technology — A Practical Guide Book
- Emerson et al. (1975) aqueous ammonia equilibrium
- WOAH Aquatic Animal Health Code
- FAO technical papers
"""
from __future__ import annotations

from typing import List, Optional

from schemas import EnvelopeCriterion, Framework, LifeStage, SystemType


def _c(name: str) -> EnvelopeCriterion:
    """Helper used only to shorten the long lists below."""
    return EnvelopeCriterion(**name) if isinstance(name, dict) else name


# ---- Generic warm-water finfish (tilapia, carps, catfish) pond envelope ----
WARM_FINFISH_POND = Framework(
    name="Warm-water finfish pond (Boyd & Tucker, 1998; Boyd, 2020)",
    species=["tilapia", "oreochromis niloticus", "catfish", "ictalurus punctatus", "carp", "cyprinus carpio"],
    system_types=[SystemType.POND],
    life_stages=[LifeStage.LARVAE, LifeStage.JUVENILE, LifeStage.ADULT],
    envelope=[
        EnvelopeCriterion(parameter="do_mg_l", unit="mg/L", min_optimal=4.0, min_stress=2.5, lethal_below=1.0,
                          source="Boyd & Tucker (1998); morning DO should remain > 4 mg/L for tilapia/catfish, < 1.5 mg/L causes acute stress"),
        EnvelopeCriterion(parameter="tan_mg_l", unit="mg/L", max_optimal=1.0, max_stress=2.5,
                          source="Boyd (2020); chronic TAN exposure > 2–3 mg/L reduces growth in warm-water fish"),
        EnvelopeCriterion(parameter="unionized_nh3_mg_l", unit="mg/L", max_stress=0.05, lethal_above=0.1,
                          source="Emerson et al. (1975) equilibrium + USEPA/AWWA warm-water fish chronic criteria"),
        EnvelopeCriterion(parameter="no2_mg_l", unit="mg/L", max_optimal=0.5, max_stress=2.0,
                          source="Boyd & Tucker (1998); nitrite toxicity is exacerbated by low Cl⁻"),
        EnvelopeCriterion(parameter="ph", unit="pH", min_optimal=6.5, max_optimal=9.0, min_stress=6.0, max_stress=9.5,
                          source="Boyd (2020); tilapia tolerate wide pH but reproduction/performance best 7–9"),
        EnvelopeCriterion(parameter="alkalinity_mg_l_caCO3", unit="mg/L CaCO3", min_optimal=50.0, min_stress=20.0,
                          source="Boyd & Tucker (1998); adequate alkalinity buffers pH and supports phytoplankton"),
        EnvelopeCriterion(parameter="temp_c", unit="°C", min_optimal=25.0, max_optimal=32.0, min_stress=18.0, max_stress=36.0,
                          source="Boyd (2020); tilapia optimal 26–30 °C"),
        EnvelopeCriterion(parameter="salinity_ppt", unit="ppt", min_optimal=0.0, max_optimal=5.0, max_stress=20.0,
                          source="Tilapia are euryhaline to ~20 ppt but freshwater growth is optimal"),
    ],
    carrying_capacity_model="Chlorophyll-a / feed-input based carrying capacity (Boyd & Tucker, 1998)",
    biosecurity_standard="WOAH Aquatic Animal Health Code, general farm biosecurity chapter",
    citations=[
        "Boyd, C.E. & Tucker, C.S. (1998). Pond Aquaculture Water Quality Management.",
        "Boyd, C.E. (2020). Water Quality: An Introduction, 3rd ed. Springer.",
        "Emerson, K., Russo, R.C., Lund, R.E. & Thurston, R.V. (1975). Aqueous ammonia equilibrium calculations: effect of pH and temperature. J Fish Res Board Can 32:2379-2383.",
        "WOAH (2024). Aquatic Animal Health Code. https://www.woah.org/en/what-we-do/standards/codes-and-manuals/aquatic-code-online-access/",
    ],
    rationale="Selected because the species is a warm-water finfish raised in earthen ponds; Boyd & Tucker is the canonical pond water-quality reference.",
)


# ---- Litopenaeus vannamei / Penaeus monodon shrimp pond envelope ----
SHRIMP_POND = Framework(
    name="Penaeid shrimp pond (Boyd & Tucker, 1998; FAO; Avnimelech, 2012)",
    species=["whiteleg shrimp", "litopenaeus vannamei", "pacific white shrimp", "black tiger shrimp", "penaeus monodon"],
    system_types=[SystemType.POND],
    life_stages=[LifeStage.LARVAE, LifeStage.JUVENILE, LifeStage.ADULT],
    envelope=[
        EnvelopeCriterion(parameter="do_mg_l", unit="mg/L", min_optimal=4.0, min_stress=2.5, lethal_below=1.5,
                          source="Boyd & Tucker (1998); shrimp ponds require DO > 4 mg/L, dawn minima < 2.5 mg/L trigger mortality"),
        EnvelopeCriterion(parameter="tan_mg_l", unit="mg/L", max_optimal=1.0, max_stress=2.0,
                          source="Boyd (2020); TAN > 2 mg/L reduces shrimp growth and molting"),
        EnvelopeCriterion(parameter="unionized_nh3_mg_l", unit="mg/L", max_stress=0.05, lethal_above=0.1,
                          source="Emerson et al. (1975) equilibrium; shrimp NH3 96-h LC50 commonly 0.3–1.0 mg/L depending on pH/temp"),
        EnvelopeCriterion(parameter="no2_mg_l", unit="mg/L", max_optimal=0.5, max_stress=1.5,
                          source="Boyd & Tucker (1998); shrimp are more sensitive to NO2⁻ than tilapia"),
        EnvelopeCriterion(parameter="ph", unit="pH", min_optimal=7.5, max_optimal=8.5, min_stress=7.0, max_stress=9.0,
                          source="FAO shrimp culture manuals; pH < 7.0 or > 9.0 stresses shrimp and ammonia toxicity rises"),
        EnvelopeCriterion(parameter="alkalinity_mg_l_caCO3", unit="mg/L CaCO3", min_optimal=80.0, min_stress=50.0,
                          source="Boyd (2020); shrimp ponds need strong buffering to counter nitrification/photosynthesis swings"),
        EnvelopeCriterion(parameter="temp_c", unit="°C", min_optimal=26.0, max_optimal=32.0, min_stress=22.0, max_stress=35.0,
                          source="FAO; L. vannamei optimal 27–30 °C"),
        EnvelopeCriterion(parameter="salinity_ppt", unit="ppt", min_optimal=5.0, max_optimal=35.0, min_stress=1.0, max_stress=40.0,
                          source="L. vannamei is euryhaline; P. monodon prefers 10–30 ppt"),
    ],
    carrying_capacity_model="Pond assimilative capacity based on DO budget, feed input, and sediment oxygen demand (Boyd & Tucker, 1998)",
    biosecurity_standard="WOAH Aquatic Animal Health Code, penaeid shrimp disease chapters (WSD, AHPND/EMS, EHP)",
    citations=[
        "Boyd, C.E. & Tucker, C.S. (1998). Pond Aquaculture Water Quality Management.",
        "Boyd, C.E. (2020). Water Quality: An Introduction.",
        "FAO (2020). Technical manual on pond culture of Penaeus vannamei.",
        "Emerson, K. et al. (1975). Aqueous ammonia equilibrium calculations. J Fish Res Board Can 32:2379-2383.",
        "WOAH (2024). Aquatic Animal Health Code — Diseases of Crustaceans.",
    ],
    rationale="Selected for penaeid shrimp in pond culture; combines pond-water-quality envelopes with crustacean-specific disease standards.",
)


# ---- Recirculating Aquaculture Systems (RAS) salmonid / high-value finfish ----
RAS_HIGH_VALUE = Framework(
    name="Recirculating Aquaculture Systems — salmonid/high-value finfish (Timmons & Guerdat, 2017)",
    species=["atlantic salmon", "salmo salar", "rainbow trout", "oncorhynchus mykiss", "yellowtail", "seriola"],
    system_types=[SystemType.RAS],
    life_stages=[LifeStage.JUVENILE, LifeStage.ADULT],
    envelope=[
        EnvelopeCriterion(parameter="do_mg_l", unit="mg/L", min_optimal=6.0, min_stress=4.0, lethal_below=3.0,
                          source="Timmons & Guerdat (2017); salmonids require high DO; 6 mg/L minimum for optimal growth"),
        EnvelopeCriterion(parameter="tan_mg_l", unit="mg/L", max_optimal=0.5, max_stress=1.0,
                          source="Timmons & Guerdat (2017); biofilter target TAN < 1 mg/L, ideally < 0.5 mg/L"),
        EnvelopeCriterion(parameter="unionized_nh3_mg_l", unit="mg/L", max_optimal=0.005, max_stress=0.025, lethal_above=0.05,
                          source="Emerson et al. (1975) + salmonid acute criteria; NH3 is the design-toxicant for RAS biofilters"),
        EnvelopeCriterion(parameter="no2_mg_l", unit="mg/L", max_optimal=0.1, max_stress=1.0,
                          source="Malone & Pfeiffer (2006); RAS nitrite should remain low; transient peaks during biofilter maturity"),
        EnvelopeCriterion(parameter="ph", unit="pH", min_optimal=7.0, max_optimal=8.0, min_stress=6.5, max_stress=8.5,
                          source="Timmons & Guerdat (2017); nitrification pH optimum 7.5–8.0"),
        EnvelopeCriterion(parameter="alkalinity_mg_l_caCO3", unit="mg/L CaCO3", min_optimal=50.0, min_stress=25.0,
                          source="Timmons & Guerdat (2017); nitrification consumes alkalinity; maintain > 50 mg/L"),
        EnvelopeCriterion(parameter="temp_c", unit="°C", min_optimal=12.0, max_optimal=16.0, min_stress=8.0, max_stress=18.0,
                          source="Salmonid optimal 12–16 °C; > 18 °C causes stress and disease susceptibility"),
        EnvelopeCriterion(parameter="salinity_ppt", unit="ppt", min_optimal=0.0, max_optimal=35.0,
                          source="Freshwater or full seawater RAS depending on species; mixed salinity is stressful"),
    ],
    carrying_capacity_model="Feed loading rate / TAN production vs biofilter volumetric nitrification rate (Timmons & Guerdat, 2017)",
    biosecurity_standard="WOAH Aquatic Animal Health Code; RAS design biosecurity (disinfection, quarantine, backup systems)",
    citations=[
        "Timmons, M.B. & Guerdat, T. (2017). Recirculating Aquaculture, 4th ed. Ithaca Publishing.",
        "Malone, R.F. & Pfeiffer, T.J. (2006). Rating fixed film nitrifying biofilters used in recirculating aquaculture systems. Aquacultural Engineering 34(3):389-402.",
        "Emerson, K. et al. (1975). Aqueous ammonia equilibrium calculations. J Fish Res Board Can 32:2379-2383.",
        "WOAH (2024). Aquatic Animal Health Code.",
    ],
    rationale="Selected for high-value finfish in fully controlled recirculating systems where ammonia is the design-toxicant and biofilter performance is critical.",
)


# ---- Biofloc Technology (BFT) envelope ----
BIOFLOC = Framework(
    name="Biofloc Technology (Avnimelech, 2012; Ebeling et al.; Emerenciano et al.)",
    species=["whiteleg shrimp", "litopenaeus vannamei", "tilapia", "oreochromis niloticus", "catfish"],
    system_types=[SystemType.BIOFLOC],
    life_stages=[LifeStage.JUVENILE, LifeStage.ADULT],
    envelope=[
        EnvelopeCriterion(parameter="do_mg_l", unit="mg/L", min_optimal=4.0, min_stress=2.0, lethal_below=1.0,
                          source="Avnimelech (2012); high oxygen demand from heterotrophic floc; aeration is non-negotiable"),
        EnvelopeCriterion(parameter="tan_mg_l", unit="mg/L", max_optimal=1.0, max_stress=3.0,
                          source="Avnimelech (2012); heterotrophic assimilation lowers TAN but spikes can occur during C:N imbalance"),
        EnvelopeCriterion(parameter="unionized_nh3_mg_l", unit="mg/L", max_stress=0.05, lethal_above=0.1,
                          source="Emerson et al. (1975) equilibrium; BFT does not eliminate NH3 toxicity"),
        EnvelopeCriterion(parameter="ph", unit="pH", min_optimal=7.0, max_optimal=8.5, min_stress=6.5, max_stress=9.0,
                          source="Avnimelech (2012); pH must be buffered; nitrification + heterotrophy drive swings"),
        EnvelopeCriterion(parameter="alkalinity_mg_l_caCO3", unit="mg/L CaCO3", min_optimal=100.0, min_stress=50.0,
                          source="Avnimelech (2012); BFT consumes more alkalinity; keep > 100 mg/L CaCO3"),
        EnvelopeCriterion(parameter="temp_c", unit="°C", min_optimal=26.0, max_optimal=32.0,
                          source="Shrimp/tilapia BFT; microbial activity falls below ~24 °C"),
        EnvelopeCriterion(parameter="salinity_ppt", unit="ppt", min_optimal=5.0, max_optimal=35.0,
                          source="Species dependent; BFT used across brackish and marine shrimp, freshwater tilapia"),
        EnvelopeCriterion(parameter="c_n_ratio", unit="ratio", min_optimal=10.0, max_optimal=15.0, min_stress=6.0, max_stress=20.0,
                          source="Avnimelech (2012); optimal C:N 10–15 for heterotrophic bacteria; too high causes excessive floc"),
        EnvelopeCriterion(parameter="tss_mg_l", unit="mg/L", min_optimal=300.0, max_optimal=500.0, min_stress=100.0, max_stress=600.0,
                          source="Emerenciano et al.; BFT floc concentration target 300–500 mg/L TSS"),
    ],
    carrying_capacity_model="Settling solids / TSS control and feed-loading capacity (Avnimelech, 2012)",
    biosecurity_standard="WOAH Aquatic Animal Health Code; closed-system BFT reduces water exchange but requires pathogen screening",
    citations=[
        "Avnimelech, Y. (2012). Biofloc Technology — A Practical Guide Book, 2nd ed. World Aquaculture Society.",
        "Ebeling, J.M., Timmons, M.B. & Bisogni, J.J. (2006). Engineering analysis of the stoichiometry of photoautotrophic, autotrophic, and heterotrophic removal of ammonia-nitrogen in aquaculture systems. Aquaculture 257:346-358.",
        "Emerenciano, G.C., Martínez-Córdova, L.R., Martínez-Porchas, M. & Miranda-Baeza, A. (2017). Biofloc Technology (BFT): A review of what we know and what we need to know. Aquacultural Engineering 77:100-117.",
        "Avnimelech, Y. (1999). Carbon/nitrogen ratio as a control element in aquaculture systems. Aquaculture 176:227-235.",
    ],
    rationale="Selected for intensive biofloc systems; floc metabolism, C:N ratio, and TSS become first-class water-quality parameters.",
)


# ---- Generic freshwater flow-through / cage ----
FLOW_THROUGH_FINFISH = Framework(
    name="Flow-through / cage freshwater finfish (Boyd, 2020; Wedemeyer, 1996)",
    species=["trout", "salmon", "carp", "tilapia", "catfish"],
    system_types=[SystemType.FLOW_THROUGH, SystemType.CAGE],
    life_stages=[LifeStage.JUVENILE, LifeStage.ADULT],
    envelope=[
        EnvelopeCriterion(parameter="do_mg_l", unit="mg/L", min_optimal=6.0, min_stress=4.0, lethal_below=2.0,
                          source="Boyd (2020); flow-through systems should maintain near-saturation DO"),
        EnvelopeCriterion(parameter="tan_mg_l", unit="mg/L", max_optimal=1.0, max_stress=2.0,
                          source="Boyd (2020)"),
        EnvelopeCriterion(parameter="unionized_nh3_mg_l", unit="mg/L", max_stress=0.05, lethal_above=0.1,
                          source="Emerson et al. (1975)"),
        EnvelopeCriterion(parameter="no2_mg_l", unit="mg/L", max_optimal=0.5, max_stress=1.5,
                          source="Boyd (2020)"),
        EnvelopeCriterion(parameter="ph", unit="pH", min_optimal=6.5, max_optimal=9.0,
                          source="Boyd (2020)"),
        EnvelopeCriterion(parameter="alkalinity_mg_l_caCO3", unit="mg/L CaCO3", min_optimal=50.0,
                          source="Boyd (2020)"),
        EnvelopeCriterion(parameter="temp_c", unit="°C", min_optimal=15.0, max_optimal=25.0,
                          source="Species-dependent; generic temperate finfish band"),
        EnvelopeCriterion(parameter="salinity_ppt", unit="ppt", min_optimal=0.0, max_optimal=0.5,
                          source="Freshwater systems only"),
    ],
    carrying_capacity_model="Hydraulic residence time and waste dilution (Timmons & Guerdat, 2017; Boyd, 2020)",
    biosecurity_standard="WOAH Aquatic Animal Health Code; site-level biosecurity for open-water cages",
    citations=[
        "Boyd, C.E. (2020). Water Quality: An Introduction.",
        "Wedemeyer, G.A. (1996). Physiology of Fish in Intensive Culture Systems. Chapman & Hall.",
        "Emerson, K. et al. (1975). Aqueous ammonia equilibrium calculations. J Fish Res Board Can 32:2379-2383.",
        "WOAH (2024). Aquatic Animal Health Code.",
    ],
    rationale="Selected for open-water or flow-through finfish where the primary controls are water exchange and DO saturation.",
)


FRAMEWORK_REGISTRY: List[Framework] = [
    WARM_FINFISH_POND,
    SHRIMP_POND,
    RAS_HIGH_VALUE,
    BIOFLOC,
    FLOW_THROUGH_FINFISH,
]


def select_framework(species: str, system_type: SystemType, life_stage: Optional[LifeStage] = None) -> Framework:
    """
    Return the most specific framework for a species/system combination.
    Falls back to the generic warm-water finfish pond framework when uncertain.
    """
    species_norm = species.strip().lower()
    system_norm = system_type.value.lower()

    # System-specific first
    if system_norm == "biofloc":
        return BIOFLOC
    if system_norm == "ras":
        return RAS_HIGH_VALUE
    if system_norm in ("flow-through", "cage"):
        return FLOW_THROUGH_FINFISH

    # Species-specific within ponds
    shrimp_keywords = {"shrimp", "litopenaeus", "penaeus", "vannamei", "monodon", "whiteleg", "pacific white"}
    if any(k in species_norm for k in shrimp_keywords):
        return SHRIMP_POND

    return WARM_FINFISH_POND


def get_framework_by_name(name: str) -> Optional[Framework]:
    for fw in FRAMEWORK_REGISTRY:
        if fw.name.lower() == name.lower():
            return fw
    return None

