"""Type-safe configuration management for the ras-coldwater-aquaculture engine.

Settings are loaded from three layers, each overriding the one below:

1. Environment variables (prefixed ``RAS_``) - highest priority.
2. JSON config files under ``config/`` (species_envelopes.json, feature_flags.json).
3. Built-in dataclass defaults.

All settings are validated at load time. Any invalid value raises a
``ConfigError`` with a human-readable message, so the rest of the codebase can
rely on invariants without re-checking. Pure standard library - no pydantic /
yaml dependency required.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CONFIG_DIR = Path(__file__).resolve().parent
ROOT_DIR = CONFIG_DIR.parent


class ConfigError(ValueError):
    """Raised when a configuration value is missing, out of range, or malformed."""


# ---------------------------------------------------------------------------
# Sub-config dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LLMSettings:
    """LLM / agent runtime parameters (used by the router & skills)."""
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.2
    max_output_tokens: int = 4096
    request_timeout_s: int = 60
    max_retries: int = 2
    backoff_base_s: float = 1.5

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ConfigError(f"temperature must be in [0,2], got {self.temperature}")
        if self.max_output_tokens <= 0:
            raise ConfigError("max_output_tokens must be positive")
        if self.max_retries < 0:
            raise ConfigError("max_retries must be >= 0")


@dataclass(frozen=True)
class LoggingSettings:
    """Structured logging configuration."""
    level: str = "INFO"
    format: str = "json"            # "json" | "text"
    log_dir: str = "logs"
    console: bool = True
    file_name: str = "ras_engine.log"

    def __post_init__(self) -> None:
        if self.format not in ("json", "text"):
            raise ConfigError(f"log format must be 'json' or 'text', got {self.format!r}")
        if self.level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ConfigError(f"invalid log level {self.level!r}")


@dataclass(frozen=True)
class FeatureFlags:
    """System-wide feature flags."""
    enable_knowledge_crawl: bool = True
    enable_web_search: bool = True
    enable_degradation_banner: bool = True
    enable_chain_of_thought_routing: bool = True
    enable_quality_gate_autofix: bool = True
    enable_token_budget_enforcement: bool = True
    enable_dry_run_safe_mode: bool = False
    strict_evidence_tracing: bool = True
    max_skill_retries: int = 2
    max_context_tokens: int = 90000
    reserved_output_tokens: int = 4000

    def __post_init__(self) -> None:
        if self.max_skill_retries < 0:
            raise ConfigError("max_skill_retries must be >= 0")
        if self.max_context_tokens <= self.reserved_output_tokens:
            raise ConfigError(
                "max_context_tokens must exceed reserved_output_tokens "
                f"({self.max_context_tokens} <= {self.reserved_output_tokens})"
            )


# ---------------------------------------------------------------------------
# Top-level settings
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Settings:
    """Immutable, validated application settings."""
    domain: str = "Recirculating Aquaculture Systems & Cold-Water Fish Health Management"
    skill_name: str = "ras-coldwater-aquaculture"
    version: str = "2.0.0"
    default_language: str = "en"
    knowledge_base_path: str = "SECOND-KNOWLEDGE-BRAIN.md"
    envelopes_path: str = "config/species_envelopes.json"
    feature_flags_path: str = "config/feature_flags.json"
    llm: LLMSettings = field(default_factory=LLMSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    species_envelopes: Dict[str, Any] = field(default_factory=dict)
    biofilter_media: Dict[str, Any] = field(default_factory=dict)

    # ----- path helpers -----
    def resolve_path(self, relative: str) -> Path:
        p = Path(relative)
        return p if p.is_absolute() else (ROOT_DIR / p)

    @property
    def knowledge_base_file(self) -> Path:
        return self.resolve_path(self.knowledge_base_path)

    @property
    def log_file(self) -> Path:
        return self.resolve_path(self.logging.log_dir) / self.logging.file_name

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # drop large blobs from serializable view
        d.pop("species_envelopes", None)
        d.pop("biofilter_media", None)
        return d


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")
    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc


def _coerce_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in ("1", "true", "yes", "on", "y"):
        return True
    if v in ("0", "false", "no", "off", "n"):
        return False
    raise ConfigError(f"cannot parse boolean from {value!r}")


def _env(name: str) -> Optional[str]:
    return os.environ.get(name)


def _build_llm() -> LLMSettings:
    kwargs: Dict[str, Any] = {}
    if (v := _env("RAS_LLM_MODEL")) is not None:
        kwargs["model"] = v
    if (v := _env("RAS_LLM_TEMPERATURE")) is not None:
        kwargs["temperature"] = float(v)
    if (v := _env("RAS_LLM_MAX_OUTPUT_TOKENS")) is not None:
        kwargs["max_output_tokens"] = int(v)
    if (v := _env("RAS_LLM_TIMEOUT")) is not None:
        kwargs["request_timeout_s"] = int(v)
    if (v := _env("RAS_LLM_MAX_RETRIES")) is not None:
        kwargs["max_retries"] = int(v)
    if (v := _env("RAS_LLM_BACKOFF_BASE")) is not None:
        kwargs["backoff_base_s"] = float(v)
    return LLMSettings(**kwargs)


def _build_logging() -> LoggingSettings:
    kwargs: Dict[str, Any] = {}
    if (v := _env("RAS_LOG_LEVEL")) is not None:
        kwargs["level"] = v.upper()
    if (v := _env("RAS_LOG_FORMAT")) is not None:
        kwargs["format"] = v.lower()
    if (v := _env("RAS_LOG_DIR")) is not None:
        kwargs["log_dir"] = v
    if (v := _env("RAS_LOG_CONSOLE")) is not None:
        kwargs["console"] = _coerce_bool(v)
    if (v := _env("RAS_LOG_FILE")) is not None:
        kwargs["file_name"] = v
    return LoggingSettings(**kwargs)


def _build_features(base: Dict[str, Any]) -> FeatureFlags:
    f = dict(base.get("features", {}))
    overrides: Dict[str, Any] = {}
    bool_keys = (
        "enable_knowledge_crawl", "enable_web_search", "enable_degradation_banner",
        "enable_chain_of_thought_routing", "enable_quality_gate_autofix",
        "enable_token_budget_enforcement", "enable_dry_run_safe_mode",
        "strict_evidence_tracing",
    )
    int_keys = ("max_skill_retries", "max_context_tokens", "reserved_output_tokens")
    env_prefix = "RAS_"
    for key in bool_keys + int_keys:
        env_name = f"{env_prefix}{key.upper()}"
        if (raw := _env(env_name)) is not None:
            overrides[key] = _coerce_bool(raw) if key in bool_keys else int(raw)
    merged = {**f, **overrides}
    # Only pass recognized keys to the dataclass.
    recognized = set(bool_keys) | set(int_keys)
    filtered = {k: v for k, v in merged.items() if k in recognized}
    return FeatureFlags(**filtered)


def load_settings(
    envelopes_path: Optional[str] = None,
    feature_flags_path: Optional[str] = None,
) -> Settings:
    """Load and validate the full settings object.

    Reads JSON config files, overlays environment variables, validates every
    field via the frozen dataclasses' ``__post_init__``, and returns an
    immutable ``Settings`` instance. Raises ``ConfigError`` on any problem.
    """
    env_path = envelopes_path or "config/species_envelopes.json"
    ff_path = feature_flags_path or "config/feature_flags.json"

    envelopes_doc = _load_json(ROOT_DIR / env_path)
    ff_doc = _load_json(ROOT_DIR / ff_path)

    features = _build_features(ff_doc)
    llm = _build_llm()
    logging_cfg = _build_logging()

    species_envelopes = envelopes_doc.get("species_envelopes", {})
    biofilter_media = envelopes_doc.get("biofilter_media", {})
    if not species_envelopes:
        raise ConfigError("species_envelopes.json contains no species_envelopes")
    if not biofilter_media:
        raise ConfigError("species_envelopes.json contains no biofilter_media")

    kwargs: Dict[str, Any] = {
        "llm": llm,
        "logging": logging_cfg,
        "features": features,
        "species_envelopes": species_envelopes,
        "biofilter_media": biofilter_media,
    }
    if (v := _env("RAS_SKILL_NAME")) is not None:
        kwargs["skill_name"] = v
    if (v := _env("RAS_DEFAULT_LANGUAGE")) is not None:
        kwargs["default_language"] = v
    if (v := _env("RAS_KNOWLEDGE_BASE_PATH")) is not None:
        kwargs["knowledge_base_path"] = v

    return Settings(**kwargs)


def reload_settings(settings: Settings, **overrides: Any) -> Settings:
    """Return a new immutable ``Settings`` with the given field overrides."""
    return replace(settings, **overrides)

