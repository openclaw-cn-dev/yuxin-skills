#!/usr/bin/env python3
"""
Configuration Loader for red-tide-algal-bloom-monitoring Skill
Provides type-safe configuration management with environment variable overrides
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Generic, Type
from dataclasses import dataclass, field
from enum import Enum

# Type variables for generic types
T = TypeVar('T')


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"
    FIFO = "fifo"
    LIFO = "lifo"
    NONE = "none"


@dataclass
class LLMConfig:
    """LLM configuration"""
    default: str = "claude-sonnet-4-6"
    fallback: str = "claude-haiku-4-5"
    temperature: float = 0.7
    max_tokens: int = 8192
    window_size: int = 200000
    reserved_output_tokens: int = 4096
    max_input_tokens: int = 159804
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_compression: bool = True
    target_compression_ratio: float = 0.3


@dataclass
class DataSourceConfig:
    """Data source configuration"""
    primary_provider: str = "copernicus"
    fallback_providers: list = field(default_factory=lambda: ["noaa", "nasa"])
    refresh_interval_hours: int = 6
    max_age_hours: int = 24


@dataclass
class QualityGateConfig:
    """Quality gate configuration"""
    enabled: bool = True
    strict_mode: bool = False
    max_auto_fix_attempts: int = 2
    evidence_sources_min: int = 3
    authoritative_sources_min: int = 1
    risk_disclosure_required: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: LogLevel = LogLevel.INFO
    format: str = "structured"
    console_enabled: bool = True
    file_enabled: bool = True
    file_path: str = "logs/skill.log"
    max_size_mb: int = 100
    backup_count: int = 5
    telemetry_enabled: bool = True
    metrics_port: int = 8080
    trace_sample_rate: float = 0.1


@dataclass
class ErrorHandlingConfig:
    """Error handling configuration"""
    graceful_degradation_enabled: bool = True
    degradation_levels: int = 5
    default_degradation_level: int = 2
    enable_knowledge_base: bool = True
    enable_cache: bool = True
    enable_simplified_analysis: bool = True
    max_retry_attempts: int = 3
    exponential_backoff: bool = True
    max_backoff_seconds: int = 60


@dataclass
class FeatureFlags:
    """Feature flags"""
    enable_ml_predictions: bool = True
    enable_satellite_imagery: bool = True
    enable_alert_system: bool = True
    enable_multi_language: bool = True
    enable_offline_mode: bool = False
    enable_beta_features: bool = False


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    enable_async_operations: bool = True
    batch_size: int = 10
    prefetch_enabled: bool = True
    cache_strategy: CacheStrategy = CacheStrategy.LRU
    cache_size_mb: int = 512


@dataclass
class SecurityConfig:
    """Security configuration"""
    encrypt_sensitive_data: bool = True
    audit_logging: bool = True
    rate_limiting_enabled: bool = True
    requests_per_minute: int = 60
    api_key_rotation_days: int = 90


@dataclass
class SkillConfig:
    """Main skill configuration container"""
    name: str = "red-tide-algal-bloom-monitoring"
    version: str = "2.0.0"
    description: str = "Red Tide (Harmful Algal Bloom) Monitoring & Early Warning"
    author: str = "972026 Skill Library"
    license: str = "MIT"
    llm: LLMConfig = field(default_factory=LLMConfig)
    data_sources: Dict[str, DataSourceConfig] = field(default_factory=dict)
    quality_gates: QualityGateConfig = field(default_factory=QualityGateConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    error_handling: ErrorHandlingConfig = field(default_factory=ErrorHandlingConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)


class ConfigLoader:
    """
    Configuration loader with environment variable override support
    Loads from YAML files and applies environment overrides
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader

        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent

        self.config_dir = Path(config_dir)
        self.default_config_path = self.config_dir / "default_config.yaml"
        self.local_config_path = self.config_dir / "local_config.yaml"
        self._config: Optional[SkillConfig] = None

    def load(self) -> SkillConfig:
        """
        Load configuration from files and environment variables

        Returns:
            SkillConfig: The loaded and validated configuration
        """
        if self._config is not None:
            return self._config

        # Load default configuration
        config_dict = self._load_yaml_file(self.default_config_path)

        # Override with local configuration if exists
        if self.local_config_path.exists():
            local_dict = self._load_yaml_file(self.local_config_path)
            config_dict = self._deep_merge(config_dict, local_dict)

        # Apply environment variable overrides
        config_dict = self._apply_env_overrides(config_dict)

        # Create typed configuration
        self._config = self._create_config_from_dict(config_dict)

        return self._config

    def _load_yaml_file(self, path: Path) -> Dict[str, Any]:
        """Load YAML file into dictionary"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}")

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration.

        Environment variables use the prefix ``RED_TIDE_SKILL_`` and mirror the
        YAML nesting with underscores, e.g. ``RED_TIDE_SKILL_LLM_MODEL_DEFAULT``
        maps to ``llm.model.default`` and ``RED_TIDE_SKILL_FEATURES_ENABLE_OFFLINE_MODE``
        maps to ``features.enable_offline_mode``.

        Because YAML leaf names may themselves contain underscores (e.g.
        ``enable_offline_mode``, ``max_input_tokens``), we cannot simply split the
        env key on ``_`` -- that would corrupt such keys. Instead we enumerate
        every leaf path present in the merged config and match each env variable
        against the set of valid, unambiguous paths. Unknown env keys are ignored
        (logged via DEBUG by the caller if needed) rather than creating stray
        branches that silently never take effect.
        """
        env_prefix = "RED_TIDE_SKILL_"
        path_index = self._build_env_path_index(config)

        for key, value in os.environ.items():
            if not key.startswith(env_prefix):
                continue
            env_key = key[len(env_prefix):].lower()
            path = path_index.get(env_key)
            if path is None:
                # No known config leaf matches this env variable; skip it so we
                # never inject a divergent branch that the typed loader ignores.
                continue
            config = self._set_nested_value(config, path, value)

        return config

    def _build_env_path_index(self, config: Dict[str, Any]) -> Dict[str, list]:
        """Build a mapping of env-style keys -> dotted path segments.

        For every leaf in ``config`` (dict nodes traversed, scalars/lists are
        leaves), record ``"_".join(path)`` -> ``path``. When two leaves collide
        on the env form (rare but possible), keep the first (shallowest) one.
        """
        index: Dict[str, list] = {}

        def walk(node: Any, path: list):
            if isinstance(node, dict):
                for k, v in node.items():
                    env_form = "_".join(path + [k])
                    if env_form not in index and not isinstance(v, dict):
                        index[env_form] = path + [k]
                    walk(v, path + [k])

        walk(config, [])
        return index

    def _set_nested_value(self, config: Dict[str, Any], keys: list, value: Any) -> Dict[str, Any]:
        """Set nested dictionary value from an explicit key path"""
        if len(keys) == 1:
            config[keys[0]] = self._convert_type(value)
            return config

        if keys[0] not in config or not isinstance(config[keys[0]], dict):
            config[keys[0]] = {}

        config[keys[0]] = self._set_nested_value(config[keys[0]], keys[1:], value)
        return config

    def _convert_type(self, value: str) -> Any:
        """Convert string value to appropriate type"""
        # Boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # Numeric
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                pass

        # String (default)
        return value

    def _create_config_from_dict(self, config_dict: Dict[str, Any]) -> SkillConfig:
        """Create typed SkillConfig from dictionary"""
        # Extract top-level configuration
        skill_config = SkillConfig(
            name=config_dict.get('skill', {}).get('name', 'red-tide-algal-bloom-monitoring'),
            version=config_dict.get('skill', {}).get('version', '2.0.0'),
            description=config_dict.get('skill', {}).get('description', ''),
            author=config_dict.get('skill', {}).get('author', ''),
            license=config_dict.get('skill', {}).get('license', 'MIT'),
        )

        # LLM configuration
        llm_dict = config_dict.get('llm', {})
        llm_config = LLMConfig(
            default=llm_dict.get('model', {}).get('default', 'claude-sonnet-4-6'),
            fallback=llm_dict.get('model', {}).get('fallback', 'claude-haiku-4-5'),
            temperature=llm_dict.get('model', {}).get('temperature', 0.7),
            max_tokens=llm_dict.get('model', {}).get('max_tokens', 8192),
            window_size=llm_dict.get('context', {}).get('window_size', 200000),
            reserved_output_tokens=llm_dict.get('context', {}).get('reserved_output_tokens', 4096),
            max_input_tokens=llm_dict.get('context', {}).get('max_input_tokens', 159804),
            enable_caching=llm_dict.get('token_management', {}).get('enable_caching', True),
            cache_ttl_seconds=llm_dict.get('token_management', {}).get('cache_ttl_seconds', 300),
            enable_compression=llm_dict.get('token_management', {}).get('enable_compression', True),
            target_compression_ratio=llm_dict.get('token_management', {}).get('target_compression_ratio', 0.3),
        )
        skill_config.llm = llm_config

        # Data sources configuration
        data_sources_config = {}
        data_sources_dict = config_dict.get('data_sources', {})
        for ds_type, ds_config in data_sources_dict.items():
            if isinstance(ds_config, dict):
                data_sources_config[ds_type] = DataSourceConfig(
                    primary_provider=ds_config.get('primary_provider', 'copernicus'),
                    fallback_providers=ds_config.get('fallback_providers', []),
                    refresh_interval_hours=ds_config.get('refresh_interval_hours', 6),
                    max_age_hours=ds_config.get('max_age_hours', 24),
                )

        if data_sources_config:
            skill_config.data_sources = data_sources_config

        # Quality gate configuration
        qg_dict = config_dict.get('quality_gates', {})
        qg_config = QualityGateConfig(
            enabled=qg_dict.get('universal', {}).get('enabled', True),
            strict_mode=qg_dict.get('universal', {}).get('strict_mode', False),
            max_auto_fix_attempts=qg_dict.get('universal', {}).get('max_auto_fix_attempts', 2),
            evidence_sources_min=qg_dict.get('domain', {}).get('custom_thresholds', {}).get('evidence_sources_min', 3),
            authoritative_sources_min=qg_dict.get('domain', {}).get('custom_thresholds', {}).get('authoritative_sources_min', 1),
            risk_disclosure_required=qg_dict.get('domain', {}).get('custom_thresholds', {}).get('risk_disclosure_required', True),
        )
        skill_config.quality_gates = qg_config

        # Logging configuration
        log_dict = config_dict.get('logging', {})
        logging_config = LoggingConfig(
            level=LogLevel(log_dict.get('level', 'INFO')),
            format=log_dict.get('format', 'structured'),
            console_enabled=log_dict.get('outputs', [{}])[0].get('enabled', True) if log_dict.get('outputs') else True,
            file_enabled=len(log_dict.get('outputs', [])) > 1 if log_dict.get('outputs') else True,
            file_path=log_dict.get('outputs', [{}])[1].get('path', 'logs/skill.log') if len(log_dict.get('outputs', [])) > 1 else 'logs/skill.log',
            max_size_mb=log_dict.get('outputs', [{}])[1].get('max_size_mb', 100) if len(log_dict.get('outputs', [])) > 1 else 100,
            backup_count=log_dict.get('outputs', [{}])[1].get('backup_count', 5) if len(log_dict.get('outputs', [])) > 1 else 5,
            telemetry_enabled=log_dict.get('telemetry', {}).get('enabled', True),
            metrics_port=log_dict.get('telemetry', {}).get('metrics_port', 8080),
            trace_sample_rate=log_dict.get('telemetry', {}).get('trace_sample_rate', 0.1),
        )
        skill_config.logging = logging_config

        # Error handling configuration
        eh_dict = config_dict.get('error_handling', {})
        error_config = ErrorHandlingConfig(
            graceful_degradation_enabled=eh_dict.get('graceful_degradation', {}).get('enabled', True),
            degradation_levels=eh_dict.get('graceful_degradation', {}).get('levels', 5),
            default_degradation_level=eh_dict.get('graceful_degradation', {}).get('default_level', 2),
            enable_knowledge_base=eh_dict.get('fallback', {}).get('enable_knowledge_base', True),
            enable_cache=eh_dict.get('fallback', {}).get('enable_cache', True),
            enable_simplified_analysis=eh_dict.get('fallback', {}).get('enable_simplified_analysis', True),
            max_retry_attempts=eh_dict.get('recovery', {}).get('max_retry_attempts', 3),
            exponential_backoff=eh_dict.get('recovery', {}).get('exponential_backoff', True),
            max_backoff_seconds=eh_dict.get('recovery', {}).get('max_backoff_seconds', 60),
        )
        skill_config.error_handling = error_config

        # Feature flags
        ff_dict = config_dict.get('features', {})
        features = FeatureFlags(
            enable_ml_predictions=ff_dict.get('enable_ml_predictions', True),
            enable_satellite_imagery=ff_dict.get('enable_satellite_imagery', True),
            enable_alert_system=ff_dict.get('enable_alert_system', True),
            enable_multi_language=ff_dict.get('enable_multi_language', True),
            enable_offline_mode=ff_dict.get('enable_offline_mode', False),
            enable_beta_features=ff_dict.get('enable_beta_features', False),
        )
        skill_config.features = features

        # Performance configuration
        perf_dict = config_dict.get('performance', {})
        performance = PerformanceConfig(
            enable_async_operations=perf_dict.get('enable_async_operations', True),
            batch_size=perf_dict.get('batch_size', 10),
            prefetch_enabled=perf_dict.get('prefetch_enabled', True),
            cache_strategy=CacheStrategy(perf_dict.get('cache_strategy', 'lru')),
            cache_size_mb=perf_dict.get('cache_size_mb', 512),
        )
        skill_config.performance = performance

        # Security configuration
        sec_dict = config_dict.get('security', {})
        security = SecurityConfig(
            encrypt_sensitive_data=sec_dict.get('encrypt_sensitive_data', True),
            audit_logging=sec_dict.get('audit_logging', True),
            rate_limiting_enabled=sec_dict.get('rate_limiting', {}).get('enabled', True),
            requests_per_minute=sec_dict.get('rate_limiting', {}).get('requests_per_minute', 60),
            api_key_rotation_days=sec_dict.get('api_key_rotation_days', 90),
        )
        skill_config.security = security

        return skill_config

    def reload(self) -> SkillConfig:
        """Force reload configuration from files"""
        self._config = None
        return self.load()

    @property
    def config(self) -> SkillConfig:
        """Get current configuration (cached)"""
        if self._config is None:
            return self.load()
        return self._config


# Global configuration instance
_config_loader: Optional[ConfigLoader] = None


def get_config(config_dir: Optional[Path] = None) -> SkillConfig:
    """Get global configuration instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_dir)
    return _config_loader.config


def reload_config(config_dir: Optional[Path] = None) -> SkillConfig:
    """Reload global configuration"""
    global _config_loader
    _config_loader = ConfigLoader(config_dir)
    return _config_loader.config


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    print(f"Loaded configuration for {config.name} v{config.version}")
    print(f"LLM Model: {config.llm.default}")
    print(f"Log Level: {config.logging.level}")
    print(f"Feature Flags: ML={config.features.enable_ml_predictions}, Satellite={config.features.enable_satellite_imagery}")
