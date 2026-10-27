"""
run_test_scenarios.py - Skill 161: ras-coldwater-aquaculture
============================================================

Production-grade structural & content validator. Verifies the 8-File
Contract deliverables, sub-skill content, the knowledge base, the test
scenarios, and quality-gate coverage against the contracts declared in
`D:\972026\SKILL-STANDARD.md` and `skills/main.md`.

Pure standard-library, no network, no side effects, deterministic - safe
for CI. Exit code 0 = all checks pass, non-zero = failures.

Usage:
    python tools/run_test_scenarios.py            # human report
    python tools/run_test_scenarios.py --all      # full suite (alias)
    python tools/run_test_scenarios.py --json     # machine-readable report
    python tools/run_test_scenarios.py --quiet     # exit code only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Dict, List

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

DOMAIN_GATES = [
    {"id": "G1", "check": "Water-quality setpoints cite >=1 authoritative aquaculture source per species+stage (FAO/DFO/Freshwater Institute/SRAC/peer-reviewed)", "fix": "Fetch setpoints from sub-evidence-collector / knowledge base"},
    {"id": "G2", "check": "Un-ionized ammonia (NH3) computed from T+pH via stated formula with units (mg/L NH3-N); flagged if above species-safe threshold", "fix": "Re-run sub-water-quality-analysis with the Emerson NH3 formula"},
    {"id": "G3", "check": "DO reported as % saturation vs temperature (not just mg/L); flagged if below species floor", "fix": "Re-run sub-water-quality-analysis with DO saturation equation"},
    {"id": "G4", "check": "Each out-of-envelope parameter maps to a concrete water-treatment action (magnitude); biofilter actions distinct from chemical/physical; cold-temperature derating applied", "fix": "Re-run sub-biofilter-disease-assessment / sub-ras-advisor with derating + action enforcement"},
    {"id": "G5", "check": "Cold-water species envelopes kept distinct (e.g. salmonids T<18 C); no warm-water setpoints applied", "fix": "Re-classify species and re-fetch the correct cold-water envelope"},
]
UNIVERSAL_GATES = ["U1", "U2", "U3", "U4", "U5", "U6"]
GATES = UNIVERSAL_GATES + [g["id"] for g in DOMAIN_GATES]
VERDICTS = ["Optimal", "Adjust Required", "Critical Alert", "Inconclusive"]

REQUIRED_FILES = [
    "CLAUDE.md", "PROJECT-detail.md", "PROJECT-DEVELOPMENT-PHASE-TRACKING.md",
    "README.md", "SECOND-KNOWLEDGE-BRAIN.md", "LICENSE",
    "skills/main.md", "tools/knowledge_updater.py", "tools/test_knowledge_updater.py",
    "tools/run_test_scenarios.py", "tools/validate_project.py",
    "tests/test-scenarios.md", "tests/TEST_RESULTS.md",
]
EXPECTED_SUBSKILLS = {
    "sub-gather-requirements", "sub-evidence-collector", "sub-water-quality-analysis",
    "sub-biofilter-disease-assessment", "sub-knowledge-updater", "sub-ras-advisor",
}
SUBSKILL_SECTIONS = ["Role & Persona", "Workflow", "Output Format", "Quality Gates"]
MAIN_SECTIONS = ["Role & Persona", "Quality Gates", "Graceful Degradation"]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---", re.S)


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class Report:
    checks: List[Check] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append(Check(name=name, passed=passed, detail=detail))

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    def failures(self) -> List[Check]:
        return [c for c in self.checks if not c.passed]


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return ""


def require(report: Report, cond: bool, label: str, detail: str = "") -> None:
    report.add(label, bool(cond), detail)


def _validate_file_structure(report: Report) -> None:
    for rel in REQUIRED_FILES:
        require(report, (ROOT / rel).exists(), f"file present: {rel}")


def _validate_subskills(report: Report) -> None:
    subs = sorted(SKILLS.glob("sub-*.md")) if SKILLS.exists() else []
    require(report, len(subs) >= 5, "at least 5 sub-skills", f"found {len(subs)}")
    got = {s.stem for s in subs}
    require(report, got == EXPECTED_SUBSKILLS, "sub-skill set", f"got {sorted(got)}")


def _validate_frontmatter_and_sections(report: Report) -> None:
    for s in sorted(SKILLS.glob("sub-*.md")):
        txt = read(s)
        m = FRONTMATTER_RE.search(txt)
        require(report, bool(m), f"{s.name}: frontmatter")
        if m:
            require(report, "name:" in m.group(1) and "description:" in m.group(1),
                     f"{s.name}: name+description")
        for sec in SUBSKILL_SECTIONS:
            require(report, sec in txt, f"{s.name}: section {sec}")

    main_txt = read(ROOT / "skills" / "main.md")
    for sec in MAIN_SECTIONS:
        require(report, sec in main_txt, f"main.md: section {sec}")
    require(report, "Harness Execution Protocol" in main_txt or "Workflow" in main_txt,
            "main.md: harness workflow heading")
    require(report, "Pre-Flight" in main_txt, "main.md: pre-flight language detection")
    require(report, "limitation" in main_txt.lower(), "main.md: limitation banner")


def _validate_quality_gates(report: Report) -> None:
    main_txt = read(ROOT / "skills" / "main.md")
    for g in GATES:
        require(report, g in main_txt, f"main.md: gate {g} present")
    # Verdicts are declared in the advisor sub-skill and referenced by main.
    adv = read(ROOT / "skills" / "sub-ras-advisor.md")
    for v in VERDICTS:
        require(report, v in adv or v in main_txt, f"advisor/verdict {v} present")


def _validate_knowledge_base(report: Report) -> None:
    brain = read(ROOT / "SECOND-KNOWLEDGE-BRAIN.md")
    require(report, "Tier 1" in brain and "Tier 4" in brain, "brain: evidence hierarchy tiers")
    dois = re.findall(r"10\.\d{4,9}/[^\s|]+", brain)
    require(report, len(dois) >= 4, "brain: >=4 DOI-cited references", f"found {len(dois)}")
    require(report, ("### 1.1" in brain) or ("Foundational" in brain) or ("## 1. Core" in brain),
            "brain: core methods present")
    require(report, "## 4. Authoritative Data Sources" in brain, "brain: data sources section")
    require(report, "## 6. Self-Update Protocol" in brain, "brain: self-update protocol")


def _validate_test_scenarios(report: Report) -> None:
    sc = read(ROOT / "tests" / "test-scenarios.md")
    require(report, sc.count("Scenario") >= 5, "scenarios: >=5", f"found {sc.count('Scenario')}")
    require(report, "degraded" in sc.lower() or "missing" in sc.lower(), "scenarios: degraded case")
    require(report, "conflict" in sc.lower() or "compare" in sc.lower() or "comparison" in sc.lower(),
            "scenarios: comparison/conflict case")
    for g in ["G1", "G2", "G3"]:
        require(report, g in sc, f"scenarios: gate {g} referenced")


def _validate_knowledge_updater(report: Report) -> None:
    ku = read(ROOT / "tools" / "knowledge_updater.py")
    for token in ["KNOWLEDGE_CONFIG", "sha256", "score_entry", "--dry-run", "validate_config"]:
        require(report, token in ku, f"knowledge_updater: {token}")


def _validate_docs(report: Report) -> None:
    pdpt = read(ROOT / "PROJECT-DEVELOPMENT-PHASE-TRACKING.md")
    require(report, "100%" in pdpt, "PDPT: 100% markers")
    require(report, "Phase 5" in pdpt, "PDPT: Phase 5")
    readme = read(ROOT / "README.md")
    require(report, "Usage" in readme, "README: usage")
    pd = read(ROOT / "PROJECT-detail.md")
    require(report, "Idea (Vietnamese)" in pd, "PROJECT-detail: Idea (Vietnamese)")
    require(report, "Harness Architecture" in pd, "PROJECT-detail: harness architecture")


def build_report() -> Report:
    report = Report()
    _validate_file_structure(report)
    _validate_subskills(report)
    _validate_frontmatter_and_sections(report)
    _validate_quality_gates(report)
    _validate_knowledge_base(report)
    _validate_test_scenarios(report)
    _validate_knowledge_updater(report)
    _validate_docs(report)
    return report


def render_human(report: Report) -> str:
    total = report.passed_count + report.failed_count
    lines = [f"[run_test_scenarios] {report.passed_count}/{total} checks passed"]
    for c in report.failures():
        lines.append(f"  - FAIL {c.name}" + (f": {c.detail}" if c.detail else ""))
    lines.append("[OK] all checks passed" if report.failed_count == 0 else "[FAIL] checks failed")
    return "\n".join(lines)


def render_json(report: Report) -> str:
    return json.dumps({
        "passed": report.passed_count,
        "failed": report.failed_count,
        "total": len(report.checks),
        "ok": report.failed_count == 0,
        "failures": [asdict(c) for c in report.failures()],
    }, indent=2)


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Structural & content validator for skill 161.")
    ap.add_argument("--all", action="store_true", help="run the full suite (alias, default behaviour)")
    ap.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    ap.add_argument("--quiet", action="store_true", help="suppress stdout; rely on exit code only")
    args = ap.parse_args(argv)

    report = build_report()
    if not args.quiet:
        print(render_json(report) if args.json else render_human(report))
    return 0 if report.failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
