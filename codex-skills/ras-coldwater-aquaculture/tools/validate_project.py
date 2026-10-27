"""
validate_project.py - Skill 161: ras-coldwater-aquaculture
8-File Contract validator (per D:\972026\SKILL-STANDARD.md).

Verifies the canonical project layout and required sections across the
8-File Contract deliverables. Exits 0 when the contract is satisfied,
non-zero with a structured report otherwise. Designed to be safe to run in
CI: pure standard-library, no network, no side effects, deterministic.

Usage:
    python tools/validate_project.py            # human report
    python tools/validate_project.py --json      # machine-readable report
    python tools/validate_project.py --quiet     # exit code only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent

# Canonical 8-File Contract layout (see SKILL-STANDARD.md section 1).
REQUIRED_FILES = [
    "CLAUDE.md",
    "PROJECT-detail.md",
    "PROJECT-DEVELOPMENT-PHASE-TRACKING.md",
    "README.md",
    "SECOND-KNOWLEDGE-BRAIN.md",
    "requirements.txt",
    ".gitignore",
    "skills/main.md",
    "tools/knowledge_updater.py",
    "tools/test_knowledge_updater.py",
    "tools/run_test_scenarios.py",
    "tests/test-scenarios.md",
    "tests/TEST_RESULTS.md",
]

# v2.0 modular architecture (skill-registry engine + modular dirs).
V2_REQUIRED_FILES = [
    "SKILL.md",
    "config/__init__.py",
    "config/settings.py",
    "config/species_envelopes.json",
    "config/feature_flags.json",
    "references/domain_guidelines.md",
    "references/citation_tiers.md",
    "references/prompt_templates/base.md",
    "references/prompt_templates/gather_requirements.md",
    "references/prompt_templates/evidence_collector.md",
    "references/prompt_templates/water_quality_analysis.md",
    "references/prompt_templates/biofilter_disease.md",
    "references/prompt_templates/knowledge_updater.md",
    "references/prompt_templates/ras_advisor.md",
    "assets/schemas/requirements.schema.json",
    "assets/schemas/water_quality_scorecard.schema.json",
    "assets/schemas/biofilter_risk.schema.json",
    "assets/schemas/verdict.schema.json",
    "assets/diagrams/architecture.mmd",
    "scripts/run_pipeline.py",
    "scripts/ingest_water_log.py",
    "scripts/seed_knowledge_base.py",
    "scripts/setup_env.py",
    "src/ras_aqua/__init__.py",
    "src/ras_aqua/engine.py",
    "src/ras_aqua/registry.py",
    "src/ras_aqua/router.py",
    "src/ras_aqua/hooks.py",
    "src/ras_aqua/tools.py",
    "src/ras_aqua/context.py",
    "src/ras_aqua/gates.py",
    "src/ras_aqua/chemistry.py",
    "src/ras_aqua/biofilter.py",
    "src/ras_aqua/diseases.py",
    "src/ras_aqua/species.py",
    "src/ras_aqua/schemas.py",
    "src/ras_aqua/errors.py",
    "src/ras_aqua/logging_config.py",
    "src/ras_aqua/llm_adapter.py",
    "src/ras_aqua/skills/__init__.py",
    "src/ras_aqua/skills/base.py",
    "src/ras_aqua/skills/gather_requirements.py",
    "src/ras_aqua/skills/evidence_collector.py",
    "src/ras_aqua/skills/water_quality_analysis.py",
    "src/ras_aqua/skills/biofilter_disease.py",
    "src/ras_aqua/skills/knowledge_updater.py",
    "src/ras_aqua/skills/ras_advisor.py",
    "tests/engine/test_chemistry.py",
    "tests/engine/test_biofilter.py",
    "tests/engine/test_diseases_species.py",
    "tests/engine/test_tools_context.py",
    "tests/engine/test_engine.py",
    ".github/workflows/ci.yml",
]

V2_REQUIRED_SECTIONS_SKILLMD = [
    "Skill Registry", "Skill Catalog", "Tool Registry", "Hooks",
    "Configuration", "Input / Output JSON Schemas", "Execution & Quality",
    "Extension Guide",
]

SKILLMD_SECTIONS = [
    "Skill Registry", "Skill Catalog", "Tool Registry", "Hooks",
    "Configuration", "Input / Output JSON Schemas", "Execution & Quality Standards",
    "Running", "Extension Guide", "Testing",
]

# Required sub-skills (Phase 1 deliverable).
REQUIRED_SUBSKILLS = [
    "sub-gather-requirements",
    "sub-evidence-collector",
    "sub-water-quality-analysis",
    "sub-biofilter-disease-assessment",
    "sub-knowledge-updater",
    "sub-ras-advisor",
]

# Required top-level README sections (SKILL-STANDARD section 5).
README_SECTIONS = [
    "Overview",
    "Features",
    "Why This Skill",
    "Installation",
    "Quick Start",
    "Usage",
    "Architecture",
    "Quality Gates",
    "Data Sources",
    "Testing",
    "Knowledge Base",
    "Roadmap",
    "Contributing",
    "License",
    "Citation",
]

# Required CLAUDE.md sections (SKILL-STANDARD section 2).
CLAUDE_SECTIONS = [
    "Skill Identity",
    "Problem This Skill Solves",
    "Harness Flow Summary",
    "Sub-Skills",
    "Tools Required",
    "Knowledge Sources",
    "Supporting Python Tools",
    "Knowledge Update Schedule",
    "Active Development Tasks",
    "References",
]

# Required PROJECT-detail.md sections (SKILL-STANDARD section 3).
PROJECT_DETAIL_SECTIONS = [
    "Executive Summary",
    "Problem Statement",
    "Target Users & Use Cases",
    "Harness Architecture",
    "Full Sub-Skill Catalog",
    "Skill File Format Specification",
    "E2E Execution Flow",
    "SECOND-KNOWLEDGE-BRAIN Integration",
    "Quality Gates Definition",
    "Test Scenarios",
    "Key Design Decisions",
    "Idea (Vietnamese)",
]

# Required PROJECT-DEVELOPMENT-PHASE-TRACKING.md phase markers.
PDPT_PHASES = ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]

# Required SECOND-KNOWLEDGE-BRAIN.md sections (SKILL-STANDARD section 9 + this domain).
BRAIN_SECTIONS = [
    "## 1. Core Concepts",
    "## 2. Key Research Papers",
    "## 3. State-of-the-Art",
    "## 4. Authoritative Data Sources",
    "## 5. Analytical Frameworks",
    "## 6. Self-Update Protocol",
    "## 7. Knowledge Update Log",
]

# Required skills/main.md sections (SKILL-STANDARD section 6).
MAIN_SECTIONS = [
    "Role & Persona",
    "Harness Execution Protocol",
    "Quality Gates",
    "Graceful Degradation",
    "Sub-skills Available",
    "Tools",
    "Output Format",
]

# Required skills/sub-*.md sections (SKILL-STANDARD section 7).
SUBSKILL_SECTIONS = ["Role & Persona", "Workflow", "Tools", "Output Format", "Quality Gates"]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?", re.S)
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s|)\]]+")


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
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    def failures(self) -> List[Check]:
        return [c for c in self.checks if not c.passed]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except OSError as exc:
        # Surface encoding/read errors rather than silently passing checks.
        return f"__READ_ERROR__: {exc}"


def has_section(text: str, section: str) -> bool:
    # Accept markdown headings (##/###) and bold labels as section markers.
    if re.search(r"(?m)^ {0,3}#{1,6}\s+" + re.escape(section) + r"\b", text):
        return True
    if re.search(r"(?m)^\s*\*\*" + re.escape(section) + r"[^\n]*\*\*\s*$", text):
        return True
    # Plain label colon fallback (e.g. "Overview" used as a paragraph lead).
    return section in text


def validate_files(report: Report) -> None:
    for rel in REQUIRED_FILES:
        target = ROOT / rel
        ok = target.exists() and target.is_file()
        report.add(f"file present: {rel}", ok, "missing" if not ok else "")


def validate_subskills(report: Report) -> None:
    skills_dir = ROOT / "skills"
    found = {p.stem for p in skills_dir.glob("sub-*.md")} if skills_dir.exists() else set()
    for name in REQUIRED_SUBSKILLS:
        present = (skills_dir / f"{name}.md").exists()
        report.add(f"sub-skill present: {name}", present, "" if present else f"got {sorted(found)}")
    # Reject unexpected extra sub-skills to keep the contract tight.
    extras = sorted(found - set(REQUIRED_SUBSKILLS))
    report.add("no extra sub-skills", len(extras) == 0, f"extras: {extras}" if extras else "")


def validate_frontmatter(report: Report) -> None:
    skills_dir = ROOT / "skills"
    mains = [skills_dir / "main.md"]
    mains += [skills_dir / f"{n}.md" for n in REQUIRED_SUBSKILLS]
    for path in mains:
        if not path.exists():
            continue
        text = read(path)
        m = FRONTMATTER_RE.search(text)
        has_fm = bool(m)
        report.add(f"{path.name}: frontmatter present", has_fm, "")
        if m:
            fm = m.group(1)
            report.add(
                f"{path.name}: frontmatter has name+description",
                re.search(r"(?m)^name:\s*\S", fm) is not None
                and re.search(r"(?m)^description:\s*\S", fm) is not None,
                "",
            )


def validate_section_sets(report: Report) -> None:
    mapping = [
        ("CLAUDE.md", "CLAUDE.md", CLAUDE_SECTIONS),
        ("PROJECT-detail.md", "PROJECT-detail.md", PROJECT_DETAIL_SECTIONS),
        ("README.md", "README.md", README_SECTIONS),
        ("skills/main.md", "skills/main.md", MAIN_SECTIONS),
    ]
    for label, rel, sections in mapping:
        text = read(ROOT / rel)
        for sec in sections:
            report.add(f"{label}: section '{sec}'", has_section(text, sec), "")

    pdpt = read(ROOT / "PROJECT-DEVELOPMENT-PHASE-TRACKING.md")
    for ph in PDPT_PHASES:
        report.add(f"PDPT: {ph}", ph in pdpt, "")
    report.add("PDPT: 100% completion marker", "100%" in pdpt, "")

    brain = read(ROOT / "SECOND-KNOWLEDGE-BRAIN.md")
    for sec in BRAIN_SECTIONS:
        report.add(f"SECOND-KNOWLEDGE-BRAIN: '{sec}'", sec in brain, "")
    dois = DOI_RE.findall(brain)
    report.add("brain: >=4 DOI-cited references", len(dois) >= 4, f"found {len(dois)}")


def validate_tools(report: Report) -> None:
    ku = read(ROOT / "tools" / "knowledge_updater.py")
    for token in ["KNOWLEDGE_CONFIG", "compute_hash", "score_entry", "fetch_with_retry", "append_to_brain", "--dry-run"]:
        report.add(f"knowledge_updater.py: contains {token}", token in ku, "")
    # Contract: a self-updating pipeline must have a runnable main entrypoint.
    report.add("knowledge_updater.py: has __main__ guard", "__name__ == \"__main__\"" in ku, "")


def validate_v2(report: Report) -> None:
    """Validate the v2.0 modular engine architecture (SKILL.md + modular dirs)."""
    for rel in V2_REQUIRED_FILES:
        target = ROOT / rel
        ok = target.exists() and target.is_file()
        report.add(f"v2 file present: {rel}", ok, "missing" if not ok else "")
    skillmd = read(ROOT / "SKILL.md")
    for sec in SKILLMD_SECTIONS:
        report.add(f"SKILL.md: section '{sec}'", has_section(skillmd, sec), "")
    # Engine smoke import: the package must import without error.
    import importlib
    import sys as _sys
    src = str(ROOT / "src")
    if src not in _sys.path:
        _sys.path.insert(0, src)
    if str(ROOT) not in _sys.path:
        _sys.path.insert(0, str(ROOT))
    try:
        eng = importlib.import_module("ras_aqua")
        ok_import = hasattr(eng, "Engine")
    except Exception as exc:
        ok_import = False
        report.add("v2: ras_aqua imports", False, str(exc))
    else:
        report.add("v2: ras_aqua imports + Engine exported", ok_import, "")
    # Quick engine run produces a verdict for a valid payload.
    if ok_import:
        try:
            engine = eng.Engine.from_config()
            rep = engine.run(requirements={
                "species": "rainbow_trout", "life_stage": "growout",
                "wq": {"T_C": 15, "DO_mgL": 5.5, "pH": 7.8, "TAN_mgL": 1.2},
                "ras_config": {"biofilter_type": "mbbr_kaldnes_k1",
                               "biofilter_area_m2": 300, "tank_volume_m3": 50},
                "biomass_kg": 2000, "feed_kg_day": 25,
                "target_objective": "health_assessment", "language": "en"})
            report.add("v2: engine run produces verdict",
                       rep.verdict is not None, rep.verdict.verdict.value if rep.verdict else "None")
        except Exception as exc:
            report.add("v2: engine run produces verdict", False, str(exc))


def build_report() -> Report:
    report = Report()
    validate_files(report)
    validate_subskills(report)
    validate_frontmatter(report)
    validate_section_sets(report)
    validate_tools(report)
    validate_v2(report)
    return report


def render_human(report: Report) -> str:
    lines = [f"[validate_project] {report.passed}/{len(report.checks)} contract checks passed"]
    for c in report.failures():
        lines.append(f"  - FAIL {c.name}" + (f": {c.detail}" if c.detail else ""))
    lines.append("[OK] 8-File Contract satisfied" if not report.failures() else "[FAIL] contract violations detected")
    return "\n".join(lines)


def render_json(report: Report) -> str:
    return json.dumps(
        {
            "passed": report.passed,
            "failed": report.failed,
            "total": len(report.checks),
            "ok": report.failed == 0,
            "failures": [asdict(c) for c in report.failures()],
        },
        indent=2,
    )


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="8-File Contract validator for skill 161.")
    ap.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    ap.add_argument("--quiet", action="store_true", help="suppress stdout; rely on exit code only")
    args = ap.parse_args(argv)

    report = build_report()
    if not args.quiet:
        print(render_json(report) if args.json else render_human(report))
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
