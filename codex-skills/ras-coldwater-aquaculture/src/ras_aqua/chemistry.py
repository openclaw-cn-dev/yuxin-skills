"""Water-chemistry computations for cold-water RAS.

All formulas are real and reference-grounded (see references/citation_tiers.md
and SECOND-KNOWLEDGE-BRAIN.md):

* Un-ionized ammonia fraction: Emerson, K. et al. (1975),
  J. Fish. Res. Board Can. 32:2379-2383 (DOI 10.1139/f75-274), Tier 2.
* Dissolved-oxygen saturation: Benson, B.B. & Krause, D. (1984),
  Limnol. Oceanogr. 29:620-632 (DOI 10.4319/lo.1984.29.3.0620), Tier 2,
  implemented via the APHA Standard Methods (2017) freshwater polynomial with
  salinity correction (Tier 1).
* Nitrification alkalinity demand: ~7.14 mg CaCO3 per mg TAN-N oxidized
  (APHA Standard Methods; Timmons & Ebeling 2013), Tier 1-2.

Pure functions, deterministic, unit-tested in tests/engine/test_chemistry.py.
"""
from __future__ import annotations

import math
from typing import Optional, Tuple

from .schemas import Severity


# ---------------------------------------------------------------------------
# Un-ionized ammonia (Emerson 1975)
# ---------------------------------------------------------------------------

def ammonia_pka(T_C: float) -> float:
    """Ammonia acid-dissociation pKa as a function of temperature (degC).

    Emerson et al. (1975): pKa(T) = 0.09018 + 2727.92 / T(K),
    where T(K) = T_C + 273.15. Valid across the aquaculture range 0-35 degC.
    """
    T_K = T_C + 273.15
    if T_K <= 0:
        raise ValueError(f"temperature must be above -273.15 degC, got {T_C}")
    return 0.09018 + 2727.92 / T_K


def unionized_ammonia_fraction(T_C: float, pH: float) -> float:
    """Fraction of total ammonia present as toxic un-ionized NH3 (0..1).

    f = 1 / (1 + 10^(pKa - pH)). Cold water raises pKa, lowering f, but
    cold-water species thresholds are far lower, so NH3 toxicity is still
    the dominant risk.
    """
    if not 0.0 <= pH <= 14.0:
        raise ValueError(f"pH out of range [0,14]: {pH}")
    pKa = ammonia_pka(T_C)
    return 1.0 / (1.0 + 10.0 ** (pKa - pH))


def unionized_ammonia_mgL(TAN_mgL: float, T_C: float, pH: float) -> Tuple[float, float]:
    """Return (NH3-N mg/L, fraction f) for a given TAN, temperature, and pH.

    NH3-N (mg/L) = TAN (mg/L) * f. Reported as NH3-N (the nitrogen mass),
    consistent with Emerson and APHA reporting conventions.
    """
    if TAN_mgL < 0:
        raise ValueError("TAN must be >= 0")
    f = unionized_ammonia_fraction(T_C, pH)
    return TAN_mgL * f, f


# ---------------------------------------------------------------------------
# Dissolved oxygen saturation (Benson & Krause 1984 / APHA 2017)
# ---------------------------------------------------------------------------

# APHA Standard Methods (2017) 4500-O coefficients for freshwater DO saturation
# at 1 atm as a function of temperature (degC). Returns mg/L.
_DO_A = (-139.34411, 1.575701e5, -6.642308e7, 1.243800e10, -8.621949e11)

# Salinity correction (APHA 4500-O): ln(DO_s) reduced by salinity term.
_DO_SAL = (0.017674, -10.754, 2140.7)  # Standard Methods salinity corr (T in Kelvin)


def do_saturation_freshwater(T_C: float, salinity_ppt: float = 0.0,
                             pressure_atm: float = 1.0) -> float:
    """Dissolved-oxygen saturation concentration (mg/L) at 1 atm, fresh water.

    Implements the APHA Standard Methods (2017) 4500-O polynomial with the
    Benson & Krause salinity correction and a simple pressure correction
    (DO_sat scales linearly with atmospheric pressure per Henry's law).
    """
    if T_C < 0 or T_C > 50:
        # Polynomial is calibrated 0-50 degC; clamp rather than fabricate.
        T_C = max(0.0, min(50.0, T_C))
    T = T_C + 273.15
    # Freshwater saturation (mg/L) at 1 atm.
    ln_dof = (
        _DO_A[0]
        + _DO_A[1] / T
        + _DO_A[2] / T**2
        + _DO_A[3] / T**3
        + _DO_A[4] / T**4
    )
    # Salinity correction (Standard Methods 4500-O; T in Kelvin).
    if salinity_ppt and salinity_ppt > 0:
        S = salinity_ppt
        sal_term = S * (_DO_SAL[0] + _DO_SAL[1] / T + _DO_SAL[2] / T**2)
        ln_dof = ln_dof - sal_term
    do_sat = math.exp(ln_dof) * pressure_atm
    return do_sat


def do_percent_saturation(DO_mgL: float, T_C: float,
                          salinity_ppt: float = 0.0,
                          pressure_atm: float = 1.0) -> float:
    """Dissolved oxygen as percent saturation vs temperature & salinity."""
    sat = do_saturation_freshwater(T_C, salinity_ppt, pressure_atm)
    if sat <= 0:
        return 0.0
    return 100.0 * DO_mgL / sat


# ---------------------------------------------------------------------------
# Nitrification alkalinity demand
# ---------------------------------------------------------------------------

ALKALINITY_PER_TAN_MG_CACO3 = 7.14
"""mg CaCO3 consumed per mg TAN oxidized during nitrification (APHA / Timmons &
Ebeling 2013). Two protons released per NH4+ -> NO3-; 7.14 mg CaCO3 neutralizes
that acidity per mg TAN-N."""


def alkalinity_demand_for_tan(tan_mgL: float, daily_water_exchange_frac: float = 0.0) -> float:
    """Daily alkalinity demand (mg/L CaCO3) to sustain nitrification of the
    measured TAN, net of any alkalinity contributed by partial water exchange.

    ``daily_water_exchange_frac`` is the make-up water fraction per day (0..1).
    """
    if tan_mgL < 0:
        raise ValueError("TAN must be >= 0")
    demand = ALKALINITY_PER_TAN_MG_CACO3 * tan_mgL
    # Make-up water of typical alkalinity ~100 mg/L contributes alkalinity;
    # model conservatively as exchange * 100 mg/L CaCO3.
    contribution = max(0.0, daily_water_exchange_frac) * 100.0
    return max(0.0, demand - contribution)


# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

def severity_for_value(value: Optional[float], alert: Optional[float],
                       critical: Optional[float], lower_is_worse: bool = False) -> Severity:
    """Map a measured value against alert/critical thresholds to a severity.

    ``lower_is_worse=True`` is used for DO (below floor is bad); default
    (False) is used for ammonia, nitrite, nitrate, CO2 (above alert is bad).
    """
    if value is None:
        return Severity.OK
    if critical is not None and alert is not None:
        if lower_is_worse:
            if value <= critical:
                return Severity.CRITICAL
            if value <= alert:
                return Severity.ALERT
        else:
            if value >= critical:
                return Severity.CRITICAL
            if value >= alert:
                return Severity.ALERT
    return Severity.OK


def severity_in_range(value: Optional[float], optimal: Optional[Tuple[float, float]],
                      safe: Optional[Tuple[float, float]]) -> Severity:
    """Severity for a ranged parameter (T, pH)."""
    if value is None:
        return Severity.OK
    if optimal and optimal[0] <= value <= optimal[1]:
        return Severity.OK
    if safe and safe[0] <= value <= safe[1]:
        return Severity.WATCH
    return Severity.ALERT
