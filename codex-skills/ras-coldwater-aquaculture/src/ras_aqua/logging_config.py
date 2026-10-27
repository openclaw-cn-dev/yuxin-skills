"""Structured, JSON-capable logging for ras_aqua.

Provides a small ``StructuredLogger`` that emits one log event per line as
either JSON (machine-parseable, default) or plain text. Designed to be
side-effect-free in dry-run mode and to rotate-free (CI-friendly); file output
is optional and created lazily.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class StructuredLogger:
    """Minimal structured logger (JSON or text) with optional file sink."""

    def __init__(self, name: str, level: str = "INFO", fmt: str = "json",
                 console: bool = True, log_file: Optional[Path] = None) -> None:
        self.name = name
        self.level = _LEVELS.get(level.upper(), logging.INFO)
        self.fmt = fmt.lower()
        self.console = console
        self.log_file = log_file
        self._file_handle = None

    # ----- public API -----
    def debug(self, event: str, **fields: Any) -> None:
        self._emit("DEBUG", event, fields)

    def info(self, event: str, **fields: Any) -> None:
        self._emit("INFO", event, fields)

    def warning(self, event: str, **fields: Any) -> None:
        self._emit("WARNING", event, fields)

    def error(self, event: str, **fields: Any) -> None:
        self._emit("ERROR", event, fields)

    def critical(self, event: str, **fields: Any) -> None:
        self._emit("CRITICAL", event, fields)

    def close(self) -> None:
        if self._file_handle is not None:
            try:
                self._file_handle.close()
            finally:
                self._file_handle = None

    # ----- internals -----
    def _emit(self, level: str, event: str, fields: Dict[str, Any]) -> None:
        if _LEVELS.get(level, logging.INFO) < self.level:
            return
        record: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": level,
            "logger": self.name,
            "event": event,
        }
        if fields:
            record["fields"] = _jsonable(fields)
        line = (
            json.dumps(record, ensure_ascii=False, default=str)
            if self.fmt == "json"
            else f"{record['ts']} [{level}] {self.name} {event} {fields}"
        )
        sink = self._file()
        if sink is not None:
            sink.write(line + "\n")
            sink.flush()
        if self.console:
            # All structured logs go to stderr so stdout stays clean for
            # machine-readable command output (e.g. run_pipeline.py JSON).
            print(line, file=sys.stderr, flush=True)

    def _file(self):
        if self.log_file is None:
            return None
        if self._file_handle is None:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                self._file_handle = self.log_file.open("a", encoding="utf-8")
            except OSError:
                self._file_handle = None
        return self._file_handle


def _jsonable(obj: Any) -> Any:
    """Best-effort conversion so json.dumps(default=str) stays predictable."""
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_jsonable(v) for v in obj]
    return str(obj)


def get_logger(name: str = "ras_aqua", settings=None) -> StructuredLogger:
    """Build a logger from a ``Settings`` instance (lazy, no hard dependency)."""
    level = "INFO"
    fmt = "json"
    console = True
    log_file: Optional[Path] = None
    if settings is not None:
        ls = getattr(settings, "logging", None)
        if ls is not None:
            level = ls.level
            fmt = ls.format
            console = ls.console
            log_file = getattr(settings, "log_file", None)
    return StructuredLogger(name, level=level, fmt=fmt, console=console,
                            log_file=log_file)
