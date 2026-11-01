"""Tests for config.config_loader (type-safe configuration management)."""
import textwrap
from pathlib import Path

import pytest

from config_loader import (
    CacheStrategy,
    ConfigLoader,
    LogLevel,
    SkillConfig,
    get_config,
)

DEFAULT_YAML = """\
skill:
  name: "red-tide-algal-bloom-monitoring"
  version: "2.1.0"
  description: "Red Tide HAB Monitoring harness"
  author: "972026 Skill Library"
  license: "MIT"
llm:
  model:
    default: "claude-sonnet-4-6"
    fallback: "claude-haiku-4-5"
    temperature: 0.7
    max_tokens: 8192
  context:
    window_size: 200000
    reserved_output_tokens: 4096
    max_input_tokens: 159804
  token_management:
    enable_caching: true
    cache_ttl_seconds: 300
    enable_compression: true
    target_compression_ratio: 0.3
data_sources:
  satellite:
    primary_provider: "copernicus"
    fallback_providers: ["noaa", "nasa"]
    refresh_interval_hours: 6
    max_age_hours: 24
quality_gates:
  universal:
    enabled: true
    strict_mode: false
    max_auto_fix_attempts: 2
  domain:
    custom_thresholds:
      evidence_sources_min: 3
      authoritative_sources_min: 1
      risk_disclosure_required: true
logging:
  level: "INFO"
  format: "structured"
  outputs:
    - type: "console"
      enabled: true
    - type: "file"
      enabled: true
      path: "logs/skill.log"
      max_size_mb: 100
      backup_count: 5
  telemetry:
    enabled: true
    metrics_port: 8080
    trace_sample_rate: 0.1
error_handling:
  graceful_degradation:
    enabled: true
    levels: 5
    default_level: 2
  fallback:
    enable_knowledge_base: true
    enable_cache: true
    enable_simplified_analysis: true
  recovery:
    max_retry_attempts: 3
    exponential_backoff: true
    max_backoff_seconds: 60
features:
  enable_ml_predictions: true
  enable_satellite_imagery: true
  enable_alert_system: true
  enable_multi_language: true
  enable_offline_mode: false
  enable_beta_features: false
performance:
  enable_async_operations: true
  batch_size: 10
  prefetch_enabled: true
  cache_strategy: "lru"
  cache_size_mb: 512
security:
  encrypt_sensitive_data: true
  audit_logging: true
  rate_limiting:
    enabled: true
    requests_per_minute: 60
  api_key_rotation_days: 90
"""


def _write_defaults(tmp_path: Path) -> Path:
    p = tmp_path / "default_config.yaml"
    p.write_text(DEFAULT_YAML, encoding="utf-8")
    return tmp_path


def test_load_returns_skill_config(tmp_path):
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert isinstance(cfg, SkillConfig)
    assert cfg.name == "red-tide-algal-bloom-monitoring"
    assert cfg.version == "2.1.0"


def test_llm_config_defaults(tmp_path):
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert cfg.llm.default == "claude-sonnet-4-6"
    assert cfg.llm.fallback == "claude-haiku-4-5"
    assert cfg.llm.temperature == pytest.approx(0.7)
    assert cfg.llm.max_tokens == 8192
    assert cfg.llm.window_size == 200000


def test_quality_gate_thresholds(tmp_path):
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert cfg.quality_gates.enabled is True
    assert cfg.quality_gates.evidence_sources_min == 3
    assert cfg.quality_gates.authoritative_sources_min == 1
    assert cfg.quality_gates.risk_disclosure_required is True


def test_feature_flags_and_performance_enums(tmp_path):
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert cfg.features.enable_ml_predictions is True
    assert cfg.features.enable_offline_mode is False
    assert cfg.performance.cache_strategy == CacheStrategy.LRU
    assert cfg.performance.batch_size == 10


def test_security_config_nested_rate_limiting(tmp_path):
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert cfg.security.rate_limiting_enabled is True
    assert cfg.security.requests_per_minute == 60
    assert cfg.security.api_key_rotation_days == 90


def test_data_sources_loaded(tmp_path):
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert "satellite" in cfg.data_sources
    assert cfg.data_sources["satellite"].primary_provider == "copernicus"
    assert cfg.data_sources["satellite"].refresh_interval_hours == 6


def test_env_override_nested_model_default(tmp_path, monkeypatch):
    # Env keys mirror the YAML nesting: LLM_MODEL_DEFAULT -> llm.model.default
    monkeypatch.setenv("RED_TIDE_SKILL_LLM_MODEL_DEFAULT", "claude-opus-test")
    monkeypatch.setenv("RED_TIDE_SKILL_FEATURES_ENABLE_OFFLINE_MODE", "true")
    monkeypatch.setenv("RED_TIDE_SKILL_PERFORMANCE_BATCH_SIZE", "42")
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert cfg.llm.default == "claude-opus-test"
    assert cfg.features.enable_offline_mode is True
    assert cfg.performance.batch_size == 42


def test_env_override_type_conversion(tmp_path, monkeypatch):
    monkeypatch.setenv("RED_TIDE_SKILL_LLM_MODEL_TEMPERATURE", "0.25")
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert cfg.llm.temperature == pytest.approx(0.25)
    assert isinstance(cfg.llm.temperature, float)


def test_env_override_boolean_and_int(tmp_path, monkeypatch):
    monkeypatch.setenv("RED_TIDE_SKILL_FEATURES_ENABLE_BETA_FEATURES", "true")
    monkeypatch.setenv("RED_TIDE_SKILL_SECURITY_API_KEY_ROTATION_DAYS", "30")
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert cfg.features.enable_beta_features is True
    assert cfg.security.api_key_rotation_days == 30
    assert isinstance(cfg.security.api_key_rotation_days, int)


def test_deep_merge_local_override(tmp_path):
    _write_defaults(tmp_path)
    (tmp_path / "local_config.yaml").write_text(textwrap.dedent("""\
        llm:
          model:
            temperature: 0.2
        features:
          enable_offline_mode: true
    """), encoding="utf-8")
    cfg = ConfigLoader(config_dir=tmp_path).load()
    assert cfg.llm.default == "claude-sonnet-4-6"  # preserved from base
    assert cfg.llm.temperature == pytest.approx(0.2)  # overridden
    assert cfg.features.enable_offline_mode is True


def test_log_level_enum_conversion(tmp_path):
    cfg = ConfigLoader(config_dir=_write_defaults(tmp_path)).load()
    assert isinstance(cfg.logging.level, LogLevel)
    assert cfg.logging.level == LogLevel.INFO


def test_global_get_config_returns_skill_config():
    # The repo's real config (default + optional local) must still load.
    cfg = get_config()
    assert isinstance(cfg, SkillConfig)
    assert cfg.name == "red-tide-algal-bloom-monitoring"
    assert cfg.version == "2.1.0"


def test_reload_refreshes_config(tmp_path, monkeypatch):
    loader = ConfigLoader(config_dir=_write_defaults(tmp_path))
    first = loader.load()
    monkeypatch.setenv("RED_TIDE_SKILL_LLM_MODEL_DEFAULT", "claude-haiku-4-5")
    second = loader.reload()
    assert second.llm.default == "claude-haiku-4-5"
    assert first.llm.default == "claude-sonnet-4-6"  # first unaffected
