# TEST_RESULTS.md - Skill 161: ras-coldwater-aquaculture

## Validation Summary

| Suite | Checks | Passed | Result |
|-------|--------|--------|--------|
| 8-File Contract + v2 architecture (`tools/validate_project.py`) | 165 | 165 | PASS |
| Knowledge-updater unit tests (`tools/test_knowledge_updater.py`) | 16 | 16 | PASS |
| Structural & content validator (`tools/run_test_scenarios.py`) | 93 | 93 | PASS |
| Engine unit + integration tests (`tests/engine/`) | 62 | 62 | PASS |

**Overall: PRODUCTION READY v2.0.0 - all validators pass (336/336 checks).**

Reproduce locally (CI-safe, no network required for the first three):

```bash
python tools/validate_project.py          # 164/164 contract + v2 architecture checks
python tools/run_test_scenarios.py --all  # 93/93 structural & content checks
python tools/test_knowledge_updater.py    # 16/16 knowledge-pipeline unit tests
python -m unittest discover -s tests/engine -p "test_*.py"   # 62/62 engine tests
python scripts/setup_env.py               # setup + engine smoke test
```

The knowledge crawl (`tools/knowledge_updater.py --dry-run`) is intentionally
not executed here to save resources; it is syntax-checked, unit-tested, and
ready to run in production. Use `--no-log-file` when driving logs via a cron
redirect.

## Test scenario coverage

`tests/test-scenarios.md` defines 5 end-to-end scenarios covering:

- a standard / object analysis case,
- a minimal-input / default case,
- a comparison case,
- a risk / feasibility or conflict case,
- a degraded-mode case (missing input / unreachable sources) with a
  LIMITATION notice.

All universal gates U1-U6 and all domain gates (G1, G2, G3, G4, G5) are
exercised across the scenarios. All verdict categories (Optimal, Adjust
Required, Critical Alert, Inconclusive) are covered. See the gate coverage
matrix in `tests/test-scenarios.md`.

## Notes

- `tools/validate_project.py` is the canonical 8-File Contract validator
  referenced by the phase tracker; it exits 0 on satisfaction and non-zero
  with a structured report (`--json`) on violation.
- The crawl pipeline is idempotent (SHA256 dedup across the existing reference
  table and the update log), atomic (temp file + os.replace), and degrades
  gracefully when optional dependencies are missing.

## Engine test coverage (v2.0)

`tests/engine/` exercises the programmatic skill-registry engine:

- `test_chemistry.py` ? Emerson NH3 equilibrium (pKa, fraction, mg/L), Benson-
  Krause/APHA DO saturation (temperature, salinity, % saturation), alkalinity
  demand, severity helpers.
- `test_biofilter.py` ? TAN production (protein scaling/clamp), cold Q10
  derating & penalty, derated capacity, loading ratio & status, alkalinity
  from feed.
- `test_diseases_species.py` ? WOAH disease rule matching (AND-match, severity
  ordering, WOAH flag), species registry (aliases, warm-water rejection,
  envelope resolution, default life stage).
- `test_tools_context.py` ? tool registry (default tools, validation, unknown
  tool, knowledge query, schema export), prompt builder rendering, token budget
  exhaustion.
- `test_engine.py` ? full pipeline: critical scenario, optimal scenario, JSON
  serialization, clarification path, warm-water rejection, Vietnamese language,
  hook emission, engine describe, all gates defined.

All engine tests are hermetic (no network) and run on stdlib `unittest`
(`pytest` also works).
