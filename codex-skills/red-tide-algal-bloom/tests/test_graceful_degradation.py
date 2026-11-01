"""Tests for scripts.graceful_degradation (multi-level degradation + fallbacks)."""
import asyncio

import pytest

from graceful_degradation import (
    DegradationBanner,
    DegradationLevel,
    DegradationTrigger,
    GracefulDegradationManager,
    reset_degradation_manager,
)


@pytest.fixture
def manager():
    reset_degradation_manager()
    return GracefulDegradationManager()


def test_default_triggers_registered(manager):
    assert len(manager.triggers) >= 6
    names = {t.name for t in manager.triggers}
    assert "satellite_api_failure" in names
    assert "all_external_sources_failed" in names


def test_no_active_triggers_returns_full_functionality(manager):
    manager.update_state()
    assert manager.state.current_level == DegradationLevel.FULL_FUNCTIONALITY
    assert manager.get_banner() == ""


def test_active_trigger_escalates_level(manager):
    trigger = DegradationTrigger(
        name="sensor_down",
        level=DegradationLevel.KNOWLEDGE_BASE_ONLY,
        condition=lambda: True,
        description="Sensor network down",
        affected_components=["sensor_data"],
    )
    manager.update_state(active_triggers=[trigger])
    assert manager.state.current_level == DegradationLevel.KNOWLEDGE_BASE_ONLY
    assert "sensor_data" in manager.state.affected_components
    banner = manager.get_banner()
    assert "REDUCED FUNCTIONALITY" in banner


def test_highest_level_among_multiple_triggers(manager):
    t1 = DegradationTrigger("a", DegradationLevel.REDUCED_DATA_AVAILABILITY,
                            lambda: True, "a", ["c1"])
    t2 = DegradationTrigger("b", DegradationLevel.MINIMUM_FUNCTIONALITY,
                            lambda: True, "b", ["c2"])
    manager.update_state(active_triggers=[t1, t2])
    assert manager.state.current_level == DegradationLevel.MINIMUM_FUNCTIONALITY


def test_check_triggers_evaluates_conditions(manager):
    trigger = DegradationTrigger("always", DegradationLevel.SIMPLIFIED_ANALYSIS,
                                 lambda: True, "always", ["x"])
    manager.register_trigger(trigger)
    active = manager.check_triggers()
    assert any(t.name == "always" for t in active)


def test_register_fallback_chain_and_execute(manager):
    calls = []

    def primary():
        raise RuntimeError("primary down")

    def secondary():
        calls.append("secondary")
        return "from-secondary"

    manager.register_fallback_chain("data", [primary, secondary])
    result = asyncio.run(manager.execute_fallback("data"))
    assert result == "from-secondary"
    assert calls == ["secondary"]


def test_fallback_all_fail_raises(manager):
    def boom():
        raise RuntimeError("nope")

    manager.register_fallback_chain("empty", [boom])
    with pytest.raises(Exception):
        asyncio.run(manager.execute_fallback("empty"))


def test_attempt_recovery(manager):
    trigger = DegradationTrigger("temp", DegradationLevel.REDUCED_DATA_AVAILABILITY,
                                 lambda: True, "temp", ["c"], auto_recovery=True)
    manager.update_state(active_triggers=[trigger])
    recovered = manager.attempt_recovery()
    assert isinstance(recovered, bool)


def test_banner_for_each_level():
    for level in DegradationLevel:
        banner = DegradationBanner.get_banner(level)
        assert isinstance(banner, str)
        # Full functionality has empty banner; others must be non-empty.
        if level != DegradationLevel.FULL_FUNCTIONALITY:
            assert banner.strip() != ""
