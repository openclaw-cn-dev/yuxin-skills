#!/usr/bin/env python3
"""
Structured Logger for red-tide-algal-bloom-monitoring Skill
Production-grade logging with context, metrics, and performance tracking
"""

import logging
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, TextIO
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import time


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    event: str
    skill: str
    context: Dict[str, Any]

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self), ensure_ascii=False)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.msg,
            "skill": getattr(record, 'skill', 'red-tide-algal-bloom-monitoring'),
            "context": getattr(record, 'context', {})
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceTracker:
    """Track performance metrics for operations"""

    def __init__(self):
        self.metrics = {}

    def start_operation(self, operation_name: str) -> float:
        """Start tracking an operation"""
        self.metrics[operation_name] = {
            'start_time': time.time(),
            'end_time': None,
            'duration_ms': None
        }
        return self.metrics[operation_name]['start_time']

    def end_operation(self, operation_name: str) -> float:
        """End tracking an operation"""
        if operation_name not in self.metrics:
            return 0.0

        end_time = time.time()
        start_time = self.metrics[operation_name]['start_time']
        duration_ms = (end_time - start_time) * 1000

        self.metrics[operation_name].update({
            'end_time': end_time,
            'duration_ms': duration_ms
        })

        return duration_ms

    def get_metric(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """Get metric for operation"""
        return self.metrics.get(operation_name)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return self.metrics.copy()

    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()


class StructuredLogger:
    """Structured logging with context and performance tracking"""

    def __init__(self, name: str = "red-tide-algal-bloom-monitoring", config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.logger = logging.getLogger(name)

        # Default configuration
        default_config = {
            'level': 'INFO',
            'format': 'structured',
            'console_enabled': True,
            'file_enabled': True,
            'file_path': 'logs/skill.log',
            'max_size_mb': 100,
            'backup_count': 5,
            'telemetry_enabled': False
        }
        self.config = {**default_config, **(config or {})}

        self.performance = PerformanceTracker()
        self._setup_logger()

    def _setup_logger(self):
        """Setup logger with handlers and formatters"""
        # Set log level
        level = getattr(logging, self.config['level'].upper(), logging.INFO)
        self.logger.setLevel(level)
        self.logger.handlers.clear()  # Clear existing handlers

        # Create formatter
        if self.config['format'] == 'structured':
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        # Console handler
        if self.config['console_enabled']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            self.logger.addHandler(console_handler)

        # File handler
        if self.config['file_enabled']:
            file_path = Path(self.config['file_path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)

            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=self.config['max_size_mb'] * 1024 * 1024,
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            self.logger.addHandler(file_handler)

    def _create_record(self, level: str, event: str, **context) -> logging.LogRecord:
        """Create a log record with context"""
        level = getattr(logging, level.upper(), logging.INFO)

        # Create log record
        record = self.logger.makeRecord(
            self.name,
            level,
            None,  # fn
            None,  # lno
            event,
            (),   # args
            None   # exc_info
        )

        # Add custom attributes
        record.skill = self.name
        record.context = context

        return record

    def log(self, level: str, event: str, **context):
        """Log structured event"""
        record = self._create_record(level, event, **context)
        self.logger.handle(record)

    def debug(self, event: str, **context):
        """Log debug event"""
        self.log('DEBUG', event, **context)

    def info(self, event: str, **context):
        """Log info event"""
        self.log('INFO', event, **context)

    def warning(self, event: str, **context):
        """Log warning event"""
        self.log('WARNING', event, **context)

    def error(self, event: str, **context):
        """Log error event"""
        self.log('ERROR', event, **context)

    def critical(self, event: str, **context):
        """Log critical event"""
        self.log('CRITICAL', event, **context)

    def log_tool_call(self, tool: str, params: Dict[str, Any], result: Any,
                     duration_ms: float, success: bool = True, error: Optional[str] = None):
        """Log tool execution"""
        context = {
            'tool': tool,
            'params': params,
            'duration_ms': duration_ms,
            'success': success
        }

        if error:
            context['error'] = error

        if success:
            self.info('tool_call', **context)
        else:
            self.error('tool_call_failed', **context)

    def log_quality_gate(self, gate: str, passed: bool, details: str,
                        auto_fixed: bool = False, retry_count: int = 0):
        """Log quality gate check"""
        self.info('quality_gate',
                 gate=gate,
                 passed=passed,
                 details=details,
                 auto_fixed=auto_fixed,
                 retry_count=retry_count)

    def log_skill_execution(self, skill_name: str, duration_ms: float,
                           degradation_level: int = 0, success: bool = True):
        """Log skill execution"""
        context = {
            'skill': skill_name,
            'duration_ms': duration_ms,
            'degradation_level': degradation_level,
            'success': success
        }

        if success:
            self.info('skill_execution', **context)
        else:
            self.error('skill_execution_failed', **context)

    def log_user_interaction(self, interaction_type: str, query: str,
                            response_length: int, satisfaction: Optional[str] = None):
        """Log user interaction"""
        context = {
            'interaction_type': interaction_type,
            'query_length': len(query),
            'response_length': response_length
        }

        if satisfaction:
            context['satisfaction'] = satisfaction

        self.info('user_interaction', **context)

    def log_degradation_event(self, level: int, trigger: str, affected_components: list):
        """Log graceful degradation event"""
        self.warning('degradation_event',
                    level=level,
                    trigger=trigger,
                    affected_components=affected_components)

    def log_cache_operation(self, operation: str, key: str, hit: bool,
                           duration_ms: Optional[float] = None):
        """Log cache operation"""
        context = {
            'operation': operation,
            'key': key,
            'hit': hit
        }

        if duration_ms is not None:
            context['duration_ms'] = duration_ms

        self.debug('cache_operation', **context)

    def log_external_api_call(self, service: str, endpoint: str,
                             duration_ms: float, success: bool,
                             status_code: Optional[int] = None,
                             error: Optional[str] = None):
        """Log external API call"""
        context = {
            'service': service,
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'success': success
        }

        if status_code is not None:
            context['status_code'] = status_code

        if error:
            context['error'] = error

        if success:
            self.info('external_api_call', **context)
        else:
            self.warning('external_api_call_failed', **context)

    @contextmanager
    def track_operation(self, operation_name: str):
        """Context manager for tracking operation duration"""
        self.performance.start_operation(operation_name)
        try:
            yield
        finally:
            duration_ms = self.performance.end_operation(operation_name)
            self.debug('operation_completed',
                     operation=operation_name,
                     duration_ms=duration_ms)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance.get_all_metrics()

    def clear_performance_metrics(self):
        """Clear performance metrics"""
        self.performance.clear_metrics()

    def set_level(self, level: str):
        """Set logging level dynamically"""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        for handler in self.logger.handlers:
            handler.setLevel(numeric_level)


class LogAggregator:
    """Aggregate logs from multiple sources"""

    def __init__(self):
        self.loggers: Dict[str, StructuredLogger] = {}

    def register_logger(self, name: str, logger: StructuredLogger):
        """Register a logger for aggregation"""
        self.loggers[name] = logger

    def get_all_logs(self, level: Optional[str] = None,
                    min_level: str = 'INFO') -> list:
        """Get all logs from registered loggers"""
        min_numeric = getattr(logging, min_level.upper(), logging.INFO)
        all_logs = []

        for logger in self.loggers.values():
            for handler in logger.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    try:
                        with open(handler.baseFilename, 'r') as f:
                            for line in f:
                                try:
                                    log_entry = json.loads(line.strip())
                                    log_level = getattr(logging, log_entry.get('level', 'INFO'))
                                    if log_level >= min_numeric:
                                        if not level or log_entry.get('level') == level.upper():
                                            all_logs.append(log_entry)
                                except json.JSONDecodeError:
                                    continue
                    except FileNotFoundError:
                        continue

        return all_logs

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error logs"""
        error_logs = self.get_all_logs(level='ERROR')
        error_count = len(error_logs)

        error_types = {}
        for log in error_logs:
            event = log.get('event', 'unknown')
            error_types[event] = error_types.get(event, 0) + 1

        return {
            'total_errors': error_count,
            'error_types': error_types,
            'recent_errors': error_logs[:10]  # Last 10 errors
        }


# Global logger instance
_logger: Optional[StructuredLogger] = None
_aggregator: Optional[LogAggregator] = None


def get_logger(name: str = "red-tide-algal-bloom-monitoring",
              config: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """Get global logger instance"""
    global _logger, _aggregator

    if _logger is None:
        _logger = StructuredLogger(name, config)
        if _aggregator is None:
            _aggregator = LogAggregator()
        _aggregator.register_logger(name, _logger)

    return _logger


def get_aggregator() -> Optional[LogAggregator]:
    """Get log aggregator"""
    global _aggregator
    if _aggregator is None:
        _aggregator = LogAggregator()
    return _aggregator


def reset_logger():
    """Reset global logger"""
    global _logger, _aggregator
    _logger = None
    _aggregator = None


if __name__ == "__main__":
    # Test logger
    logger = get_logger()

    # Test basic logging
    logger.info("Test info message", test_param="test_value")
    logger.warning("Test warning message", warning_type="test")
    logger.error("Test error message", error_code="TEST001")

    # Test tool call logging
    logger.log_tool_call(
        tool="test_tool",
        params={"query": "test"},
        result={"status": "success"},
        duration_ms=123.45,
        success=True
    )

    # Test quality gate logging
    logger.log_quality_gate(
        gate="U1",
        passed=True,
        details="≥3 sources cited",
        auto_fixed=False
    )

    # Test performance tracking
    with logger.track_operation("test_operation"):
        import time
        time.sleep(0.1)

    # Get performance metrics
    metrics = logger.get_performance_metrics()
    print(f"Performance metrics: {metrics}")

    # Test error summary
    aggregator = get_aggregator()
    summary = aggregator.get_error_summary()
    print(f"Error summary: {summary}")

    print("Logger test complete")
