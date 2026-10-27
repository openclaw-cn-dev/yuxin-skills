"""Species envelope registry and lookup for cold-water RAS species.

Loads the validated envelopes from ``config/species_envelopes.json`` (via
``Settings``) and exposes typed access for the analysis skills. Also provides
species-name normalization so free-text user input maps to canonical keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .errors import InputValidationError


# Canonical species aliases for normalization (lowercase, stripped).
SPECIES_ALIASES: Dict[str, str] = {
    "rainbow_trout": "rainbow_trout",
    "rainbow trout": "rainbow_trout",
    "oncorhynchus mykiss": "rainbow_trout",
    "trout": "rainbow_trout",
    "atlantic_salmon": "atlantic_salmon",
    "atlantic salmon": "atlantic_salmon",
    "salmo salar": "atlantic_salmon",
    "salmon": "atlantic_salmon",
    "arctic_char": "arctic_char",
    "arctic char": "arctic_char",
    "salvelinus alpinus": "arctic_char",
    "char": "arctic_char",
    "sturgeon": "sturgeon",
    "acipenser": "sturgeon",
}

WARM_WATER_HINTS = ("tilapia", "catfish", "pangasius", "pangasius", "carp",
                    "oreochromis", "ictalurus")


@dataclass
class EnvelopeLookup:
    """A resolved envelope for a species + life stage."""
    species: str
    life_stage: str
    common_name: str
    envelope: Dict[str, Any]


class SpeciesRegistry:
    """Typed accessor over the species envelope config."""

    def __init__(self, envelopes: Dict[str, Any], biofilter_media: Dict[str, Any]) -> None:
        self._envelopes = envelopes or {}
        self._biofilter_media = biofilter_media or {}

    @classmethod
    def from_settings(cls, settings) -> "SpeciesRegistry":
        return cls(settings.species_envelopes, settings.biofilter_media)

    # ----- species -----
    def normalize_species(self, raw: str) -> str:
        if not raw:
            raise InputValidationError("species is required")
        key = raw.strip().lower()
        if key in WARM_WATER_HINTS:
            raise InputValidationError(
                f"'{raw}' is a warm-water species; this skill only handles "
                "cold-water species (rainbow_trout, atlantic_salmon, "
                "arctic_char, sturgeon)."
            )
        if key in SPECIES_ALIASES:
            return SPECIES_ALIASES[key]
        # Try exact canonical match.
        if key in self._envelopes:
            return key
        raise InputValidationError(
            f"unknown species '{raw}'. Known cold-water species: "
            + ", ".join(sorted(self._envelopes.keys()))
        )

    def list_species(self) -> List[str]:
        return sorted(self._envelopes.keys())

    def life_stages(self, species: str) -> List[str]:
        sp = self._envelopes.get(species)
        if not sp:
            raise InputValidationError(f"unknown species '{species}'")
        return list(sp.get("life_stages", {}).keys())

    def common_name(self, species: str) -> str:
        sp = self._envelopes.get(species)
        return sp.get("common_name", species) if sp else species

    def resolve_envelope(self, species: str, life_stage: Optional[str]) -> EnvelopeLookup:
        sp = self._envelopes.get(species)
        if not sp:
            raise InputValidationError(f"unknown species '{species}'")
        stages = sp.get("life_stages", {})
        if life_stage and life_stage in stages:
            stage_key = life_stage
        elif stages:
            stage_key = next(iter(stages))  # default to first defined stage
        else:
            raise InputValidationError(f"no life stages defined for '{species}'")
        return EnvelopeLookup(
            species=species,
            life_stage=stage_key,
            common_name=sp.get("common_name", species),
            envelope=stages[stage_key],
        )

    # ----- biofilter media -----
    def media(self, media_key: str) -> Dict[str, Any]:
        if media_key not in self._biofilter_media:
            raise InputValidationError(
                f"unknown biofilter media '{media_key}'. Known: "
                + ", ".join(sorted(self._biofilter_media.keys()))
            )
        return self._biofilter_media[media_key]

    def list_media(self) -> List[str]:
        return sorted(self._biofilter_media.keys())

    # ----- typed envelope helpers -----
    @staticmethod
    def optimal_range(env: Dict[str, Any], param: str) -> Optional[Tuple[float, float]]:
        node = env.get(param, {})
        opt = node.get("optimal")
        if opt and len(opt) == 2:
            return (float(opt[0]), float(opt[1]))
        return None

    @staticmethod
    def safe_range(env: Dict[str, Any], param: str) -> Optional[Tuple[float, float]]:
        node = env.get(param, {})
        safe = node.get("safe")
        if safe and len(safe) == 2:
            return (float(safe[0]), float(safe[1]))
        return None

    @staticmethod
    def threshold(env: Dict[str, Any], param: str, key: str) -> Optional[float]:
        node = env.get(param, {})
        v = node.get(key)
        return float(v) if v is not None else None
