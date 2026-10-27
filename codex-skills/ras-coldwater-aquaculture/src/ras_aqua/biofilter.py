"""Biofilter engineering computations for cold-water RAS.

Reference-grounded (see references/citation_tiers.md):
* TAN production from feed: Timmons & Ebeling (2013), Recirculating
  Aquaculture, 3rd ed. (Tier 2) ? ~30-40 g TAN per kg feed at ~40% protein.
* Temperature dependence of nitrification: Zhu & Chen (2002),
  Aquaculture 213:121-130 (DOI 10.1016/S0044-8486(02)00051-8), Tier 2;
  Eding et al. (2006), Aquac. Eng. 34:364-376 (DOI 10.1016/j.aquaeng.2005.09.003), Tier 2.
* Alkalinity demand: APHA Standard Methods (2017) (Tier 1).

Pure, deterministic, unit-tested in tests/engine/test_biofilter.py.
"""
from __future__ import annotations

import math
from typing import Optional

from .schemas import Severity


# ---------------------------------------------------------------------------
# TAN production
# ---------------------------------------------------------------------------

DEFAULT_TAN_PER_KG_FEED_G = 35.0
"""g TAN produced per kg feed at a reference protein content of 40%.

Range 30-40 g/kg depending on protein and digestibility; 35 g/kg is the
commonly cited midpoint (Timmons & Ebeling 2013)."""
REFERENCE_PROTEIN_PCT = 40.0


def tan_production_from_feed(feed_kg_day: float,
                             protein_pct: Optional[float] = None) -> float:
    """Daily TAN production (g/day) from feed load.

    Scales linearly with protein fraction relative to the 40% reference,
    clamped to a biologically plausible 25-50% protein band.
    """
    if feed_kg_day < 0:
        raise ValueError("feed_kg_day must be >= 0")
    prot = protein_pct if protein_pct is not None else REFERENCE_PROTEIN_PCT
    prot = max(25.0, min(50.0, float(prot)))
    scale = prot / REFERENCE_PROTEIN_PCT
    return DEFAULT_TAN_PER_KG_FEED_G * feed_kg_day * scale


# ---------------------------------------------------------------------------
# Nitrification temperature derating
# ---------------------------------------------------------------------------

REF_TEMP_C = 25.0
"""Reference temperature at which media-specific capacities are quoted."""
Q10 = 2.0
"""Approximate Q10 for nitrification (LAWs of biological kinetics): a 10 degC
drop roughly halves the rate. Calibrated against Zhu & Chen (2002)."""


def nitrification_derating_factor(T_C: float, ref_temp_C: float = REF_TEMP_C) -> float:
    """Multiplicative derating factor for nitrification capacity vs temperature.

    Uses a Q10 model: f = Q10^((T - T_ref)/10). Below 15 degC the cold-water
    penalty becomes large (e.g. ~0.25 at 10 degC). Saturates at 1.0 above the
    reference temperature (do not over-credit warm operation beyond reference).
    """
    if T_C <= 0:
        return 0.0
    factor = Q10 ** ((T_C - ref_temp_C) / 10.0)
    return max(0.0, min(1.0, factor))


def nitrification_penalty_pct(T_C: float, ref_temp_C: float = REF_TEMP_C) -> float:
    """Capacity penalty in percent (0-100) due to cold-water operation."""
    return round((1.0 - nitrification_derating_factor(T_C, ref_temp_C)) * 100.0, 1)


# ---------------------------------------------------------------------------
# Biofilter capacity & loading
# ---------------------------------------------------------------------------

def biofilter_capacity_derated(media_area_m2: float, ref_capacity_g_per_m2_day: float,
                               T_C: float, ref_temp_C: float = REF_TEMP_C) -> float:
    """Derated biofilter TAN removal capacity (g TAN/day).

    capacity = media_area * ref_capacity * derating_factor.
    """
    if media_area_m2 < 0:
        raise ValueError("media_area_m2 must be >= 0")
    return media_area_m2 * ref_capacity_g_per_m2_day * nitrification_derating_factor(T_C, ref_temp_C)


def biofilter_loading_ratio(tan_produced_g_day: float,
                            capacity_g_day: float) -> Optional[float]:
    """Loading ratio = TAN produced / biofilter capacity. None if no capacity."""
    if not capacity_g_day or capacity_g_day <= 0:
        return None
    return tan_produced_g_day / capacity_g_day


def biofilter_status_from_ratio(ratio: Optional[float]) -> str:
    """Qualitative capacity status from the loading ratio.

    <0.7 adequate headroom; 0.7-1.0 marginal; >1.0 overloaded; unknown if no
    capacity estimate is possible.
    """
    if ratio is None:
        return "unknown"
    if ratio < 0.7:
        return "adequate"
    if ratio <= 1.0:
        return "marginal"
    return "overloaded"


# ---------------------------------------------------------------------------
# Alkalinity demand from feed
# ---------------------------------------------------------------------------

def alkalinity_demand_from_feed(feed_kg_day: float,
                                protein_pct: Optional[float] = None,
                                tank_volume_m3: Optional[float] = None,
                                daily_exchange_frac: float = 0.0) -> Optional[float]:
    """Daily alkalinity demand (mg/L CaCO3) to buffer nitrification of the
    feed-derived TAN, net of make-up water contribution.

    Returns None if tank volume is unknown (cannot express as a concentration).
    """
    tan_g_day = tan_production_from_feed(feed_kg_day, protein_pct)
    # g TAN/day -> mg TAN/day -> mg TAN/L if tank volume known.
    if not tank_volume_m3 or tank_volume_m3 <= 0:
        return None
    tan_mgL = (tan_g_day * 1000.0) / (tank_volume_m3 * 1000.0)  # mg/L
    from .chemistry import alkalinity_demand_for_tan
    return alkalinity_demand_for_tan(tan_mgL, daily_exchange_frac)


# ---------------------------------------------------------------------------
# DO requirement of the biofilter
# ---------------------------------------------------------------------------

BIOFILTER_DO_FLOOR_MGL = 4.0
"""Nitrification collapses below ~4-5 mg/L DO in the biofilter (Timmons &
Ebeling 2013)."""


def biofilter_do_status(biofilter_inlet_do_mgL: Optional[float]) -> Severity:
    if biofilter_inlet_do_mgL is None:
        return Severity.OK
    if biofilter_inlet_do_mgL <= BIOFILTER_DO_FLOOR_MGL:
        return Severity.CRITICAL
    if biofilter_inlet_do_mgL <= 5.0:
        return Severity.ALERT
    return Severity.OK
