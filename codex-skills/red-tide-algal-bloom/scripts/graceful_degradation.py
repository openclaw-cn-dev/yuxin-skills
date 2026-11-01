#!/usr/bin/env python3
"""
Graceful Degradation for red-tide-algal-bloom-monitoring Skill
Handles failures elegantly with multi-level degradation and fallback mechanisms
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class DegradationLevel(Enum):
    """Degradation levels for graceful failure handling"""
    FULL_FUNCTIONALITY = 0
    REDUCED_DATA_AVAILABILITY = 1
    KNOWLEDGE_BASE_ONLY = 2
    SIMPLIFIED_ANALYSIS = 3
    MINIMUM_FUNCTIONALITY = 4


@dataclass
class DegradationTrigger:
    """Definition of a degradation trigger"""
    name: str
    level: DegradationLevel
    condition: Callable[[], bool]
    description: str
    affected_components: List[str] = field(default_factory=list)
    auto_recovery: bool = True
    recovery_action: Optional[Callable] = None


@dataclass
class DegradationState:
    """Current degradation state"""
    current_level: DegradationLevel = DegradationLevel.FULL_FUNCTIONALITY
    active_triggers: List[DegradationTrigger] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    affected_components: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)


class DegradationBanner:
    """Banners for degradation levels"""

    BANNERS = {
        DegradationLevel.FULL_FUNCTIONALITY: "",

        DegradationLevel.REDUCED_DATA_AVAILABILITY: (
            "⚠️ **LIMITED DATA AVAILABILITY** - Using cached data and knowledge base. "
            "Some satellite/sensor data unavailable. Analysis may be based on slightly outdated information."
        ),

        DegradationLevel.KNOWLEDGE_BASE_ONLY: (
            "⚠️ **REDUCED FUNCTIONALITY** - External data sources unavailable. "
            "Analysis based on knowledge base only. Recommendations may not reflect current conditions."
        ),

        DegradationLevel.SIMPLIFIED_ANALYSIS: (
            "⚠️ **SIMPLIFIED ANALYSIS** - Full analysis unavailable. "
            "Providing basic assessment with reduced detail. Consult authoritative sources for complete guidance."
        ),

        DegradationLevel.MINIMUM_FUNCTIONALITY: (
            "⚠️ **MINIMUM FUNCTIONALITY** - Multiple system failures detected. "
            "Output requires verification with authoritative sources before use. Analysis may be incomplete."
        )
    }

    @classmethod
    def get_banner(cls, level: DegradationLevel) -> str:
        """Get banner for degradation level"""
        return cls.BANNERS.get(level, "")

    @classmethod
    def format_banner(cls, level: DegradationLevel, markdown: bool = True) -> str:
        """Format banner for output"""
        banner = cls.get_banner(level)
        if not banner:
            return ""

        if markdown:
            return f"\n{banner}\n\n"
        else:
            return f"\n{banner.replace('**', '').replace('⚠️', 'WARNING:')}\n\n"


class FallbackChain:
    """Fallback chain for resource access"""

    def __init__(self):
        self.chain: List[Callable] = []
        self.last_success: Optional[int] = None
        self.failure_counts: Dict[int, int] = {}

    def add_fallback(self, fallback: Callable, priority: int = 0):
        """Add a fallback to the chain"""
        self.chain.append((priority, fallback))
        self.chain.sort(key=lambda x: x[0])  # Sort by priority
        self.failure_counts[priority] = 0

    async def execute(self, *args, **kwargs) -> Any:
        """Execute fallback chain"""
        for priority, fallback in self.chain:
            try:
                result = fallback(*args, **kwargs)
                self.last_success = priority
                return result
            except Exception as e:
                self.failure_counts[priority] = self.failure_counts.get(priority, 0) + 1
                continue

        raise Exception("All fallbacks failed")

    def get_stats(self) -> Dict[str, Any]:
        """Get fallback statistics"""
        return {
            'last_success': self.last_success,
            'failure_counts': self.failure_counts.copy(),
            'chain_length': len(self.chain)
        }


class GracefulDegradationManager:
    """Manages graceful degradation and fallback mechanisms"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            'enabled': True,
            'max_level': DegradationLevel.MINIMUM_FUNCTIONALITY,
            'auto_recovery': True,
            'recovery_check_interval_seconds': 300,
            'default_degradation_level': DegradationLevel.REDUCED_DATA_AVAILABILITY
        }
        self.config = {**default_config, **(config or {})}

        self.state = DegradationState()
        self.triggers: List[DegradationTrigger] = []
        self.fallback_chains: Dict[str, FallbackChain] = {}

        self._setup_default_triggers()

    def _setup_default_triggers(self):
        """Setup default degradation triggers"""
        default_triggers = [
            DegradationTrigger(
                name="satellite_api_failure",
                level=DegradationLevel.REDUCED_DATA_AVAILABILITY,
                condition=lambda: False,  # Would check actual API status
                description="Satellite data API unavailable",
                affected_components=["satellite_data", "chlorophyll_analysis"],
                auto_recovery=True
            ),
            DegradationTrigger(
                name="sensor_network_unavailable",
                level=DegradationLevel.REDUCED_DATA_AVAILABILITY,
                condition=lambda: False,  # Would check sensor network
                description="In-situ sensor network unavailable",
                affected_components=["sensor_data", "in_situ_analysis"],
                auto_recovery=True
            ),
            DegradationTrigger(
                name="authoritative_sources_timeout",
                level=DegradationLevel.KNOWLEDGE_BASE_ONLY,
                condition=lambda: False,  # Would check authoritative sources
                description="Authoritative sources timeout",
                affected_components=["evidence_collector", "document_retrieval"],
                auto_recovery=True
            ),
            DegradationTrigger(
                name="knowledge_base_corrupted",
                level=DegradationLevel.SIMPLIFIED_ANALYSIS,
                condition=lambda: False,  # Would check KB integrity
                description="Knowledge base access issues",
                affected_components=["knowledge_updater", "evidence_surface"],
                auto_recovery=True
            ),
            DegradationTrigger(
                name="all_external_sources_failed",
                level=DegradationLevel.MINIMUM_FUNCTIONALITY,
                condition=lambda: False,  # Would check all sources
                description="All external data sources failed",
                affected_components=["all_external"],
                auto_recovery=True
            ),
            DegradationTrigger(
                name="llm_rate_limit",
                level=DegradationLevel.KNOWLEDGE_BASE_ONLY,
                condition=lambda: False,  # Would check rate limits
                description="LLM API rate limit exceeded",
                affected_components=["core_analysis", "synthesis"],
                auto_recovery=True
            ),
            DegradationTrigger(
                name="context_window_exceeded",
                level=DegradationLevel.SIMPLIFIED_ANALYSIS,
                condition=lambda: False,  # Would check context size
                description="Context window exceeded",
                affected_components=["main_harness", "quality_gates"],
                auto_recovery=True
            )
        ]

        for trigger in default_triggers:
            self.register_trigger(trigger)

    def register_trigger(self, trigger: DegradationTrigger):
        """Register a degradation trigger"""
        self.triggers.append(trigger)

    def check_triggers(self) -> List[DegradationTrigger]:
        """Check all triggers and return active ones"""
        active_triggers = []
        for trigger in self.triggers:
            try:
                if trigger.condition():
                    active_triggers.append(trigger)
            except Exception:
                continue  # Skip triggers that fail to check
        return active_triggers

    def update_state(self, active_triggers: Optional[List[DegradationTrigger]] = None):
        """Update degradation state based on active triggers"""
        if active_triggers is None:
            active_triggers = self.check_triggers()

        if not active_triggers:
            # No active triggers, return to full functionality
            self.state = DegradationState(
                current_level=DegradationLevel.FULL_FUNCTIONALITY,
                active_triggers=[],
                timestamp=datetime.utcnow().isoformat()
            )
            return

        # Find highest degradation level among active triggers (compare
        # the numeric .value because DegradationLevel is a plain Enum, not
        # an IntEnum, so the enum members themselves are not orderable).
        max_level = max(
            active_triggers, key=lambda t: t.level.value
        ).level

        # Collect affected components
        affected = set()
        for trigger in active_triggers:
            affected.update(trigger.affected_components)

        # Generate mitigation actions
        mitigations = self._generate_mitigations(active_triggers)

        # Update state
        self.state = DegradationState(
            current_level=max_level,
            active_triggers=active_triggers,
            timestamp=datetime.utcnow().isoformat(),
            affected_components=list(affected),
            mitigation_actions=mitigations
        )

    def _generate_mitigations(self, triggers: List[DegradationTrigger]) -> List[str]:
        """Generate mitigation actions for triggers"""
        mitigations = []

        for trigger in triggers:
            if trigger.level == DegradationLevel.REDUCED_DATA_AVAILABILITY:
                mitigations.append("Use cached data where available")
                mitigations.append("Extend knowledge base coverage")
            elif trigger.level == DegradationLevel.KNOWLEDGE_BASE_ONLY:
                mitigations.append("Rely on knowledge base only")
                mitigations.append("Provide historical analysis")
            elif trigger.level == DegradationLevel.SIMPLIFIED_ANALYSIS:
                mitigations.append("Simplify analysis to core methods")
                mitigations.append("Reduce detail in output")
            elif trigger.level == DegradationLevel.MINIMUM_FUNCTIONALITY:
                mitigations.append("Provide minimal viable output")
                mitigations.append("Flag for manual verification")

        return list(set(mitigations))  # Remove duplicates

    def get_banner(self, markdown: bool = True) -> str:
        """Get current degradation banner"""
        return DegradationBanner.format_banner(
            self.state.current_level,
            markdown=markdown
        )

    def register_fallback_chain(self, name: str, chain: List[Callable]):
        """Register a fallback chain for a resource"""
        fallback_chain = FallbackChain()
        for i, fallback in enumerate(chain):
            fallback_chain.add_fallback(fallback, priority=i)
        self.fallback_chains[name] = fallback_chain

    async def execute_fallback(self, chain_name: str, *args, **kwargs) -> Any:
        """Execute a fallback chain"""
        if chain_name not in self.fallback_chains:
            raise ValueError(f"Unknown fallback chain: {chain_name}")

        return await self.fallback_chains[chain_name].execute(*args, **kwargs)

    def attempt_recovery(self) -> bool:
        """Attempt to recover from current degradation"""
        if not self.state.active_triggers:
            return True  # Already recovered

        recovered = True

        for trigger in self.state.active_triggers:
            if trigger.auto_recovery and trigger.recovery_action:
                try:
                    trigger.recovery_action()
                    # Check if trigger is still active
                    if not trigger.condition():
                        continue  # Successfully recovered
                    else:
                        recovered = False
                except Exception:
                    recovered = False
            else:
                recovered = False

        if recovered:
            # Clear triggers and reset state
            self.state = DegradationState(
                current_level=DegradationLevel.FULL_FUNCTIONALITY,
                active_triggers=[],
                timestamp=datetime.utcnow().isoformat()
            )

        return recovered

    def get_status(self) -> Dict[str, Any]:
        """Get current degradation status"""
        return {
            'current_level': self.state.current_level.value,
            'level_name': self.state.current_level.name,
            'active_triggers': [t.name for t in self.state.active_triggers],
            'affected_components': self.state.affected_components,
            'mitigation_actions': self.state.mitigation_actions,
            'timestamp': self.state.timestamp,
            'banner': self.get_banner(markdown=False)
        }

    def save_state(self, filepath: Path):
        """Save current degradation state to file"""
        state_data = {
            'current_level': self.state.current_level.value,
            'active_triggers': [t.name for t in self.state.active_triggers],
            'timestamp': self.state.timestamp,
            'affected_components': self.state.affected_components,
            'mitigation_actions': self.state.mitigation_actions
        }

        with open(filepath, 'w') as f:
            json.dump(state_data, f, indent=2)

    def load_state(self, filepath: Path):
        """Load degradation state from file"""
        if not filepath.exists():
            return

        with open(filepath, 'r') as f:
            state_data = json.load(f)

        self.state.current_level = DegradationLevel(state_data.get('current_level', 0))
        self.state.timestamp = state_data.get('timestamp', datetime.utcnow().isoformat())
        self.state.affected_components = state_data.get('affected_components', [])
        self.state.mitigation_actions = state_data.get('mitigation_actions', [])

        # Restore active triggers
        trigger_names = state_data.get('active_triggers', [])
        self.state.active_triggers = [
            t for t in self.triggers if t.name in trigger_names
        ]


# Global degradation manager instance
_degradation_manager: Optional[GracefulDegradationManager] = None


def get_degradation_manager(config: Optional[Dict[str, Any]] = None) -> GracefulDegradationManager:
    """Get global degradation manager instance"""
    global _degradation_manager
    if _degradation_manager is None:
        _degradation_manager = GracefulDegradationManager(config)
    return _degradation_manager


def reset_degradation_manager():
    """Reset global degradation manager"""
    global _degradation_manager
    _degradation_manager = None


if __name__ == "__main__":
    # Test degradation manager
    manager = GracefulDegradationManager()

    # Test trigger registration
    def test_condition():
        return True  # Simulate trigger activation

    test_trigger = DegradationTrigger(
        name="test_trigger",
        level=DegradationLevel.SIMPLIFIED_ANALYSIS,
        condition=test_condition,
        description="Test trigger",
        affected_components=["test_component"]
    )
    manager.register_trigger(test_trigger)

    # Check triggers
    manager.update_state()
    status = manager.get_status()
    print(f"Degradation status: {status}")

    # Get banner
    banner = manager.get_banner()
    print(f"Banner: {banner}")

    # Test fallback chain
    def fallback1():
        raise Exception("Fallback 1 failed")

    def fallback2():
        return "Fallback 2 success"

    manager.register_fallback_chain("test_chain", [fallback1, fallback2])

    # Note: Can't test async execution in __main__ without async
    print("Degradation manager test complete")
