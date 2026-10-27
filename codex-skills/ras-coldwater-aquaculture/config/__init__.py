"""ras-coldwater-aquaculture configuration package.

Type-safe, environment-driven configuration management for the RAS cold-water
aquaculture skill engine. All settings are validated at load time and exposed
as frozen dataclasses so the rest of the codebase can rely on them without
defensive re-checks.
"""
from __future__ import annotations

from .settings import Settings, LLMSettings, LoggingSettings, FeatureFlags, load_settings

__all__ = [
    "Settings",
    "LLMSettings",
    "LoggingSettings",
    "FeatureFlags",
    "load_settings",
]
