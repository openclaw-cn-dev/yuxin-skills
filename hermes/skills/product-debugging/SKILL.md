---
name: product-debugging
description: Project-specific debugging playbooks for LookForge, 鱼乐宝 (FishSim), and other 渔芯科技 internal products. Each entry is a hard-won debugging methodology for a specific component — load only when working on that product.
version: 1.0.0
metadata:
  hermes:
    tags: [debugging, lookforge, fishsim, 渔芯科技, project-specific]
---

# Product Debugging Playbooks

Class-level umbrella for **project-specific debugging methodologies** we've built up across 渔芯科技 products. These are NOT general debugging guides — they're tailored to a specific codebase's quirks.

## When to use this skill

- You're debugging a LookForge backend issue (PhaseOrchestrator, SkillDispatcher, ChromaDB integration, etc.)
- You're debugging a 鱼乐宝 simulation calculation (growth model, FCR, feeding logic)
- You're hitting a known recurring issue in a 渔芯 product that has a documented fix here

**NOT for**: generic Python debugging, general ChromaDB errors (use `bugfix` umbrella instead), generic software-development methodology (use `software-development/` umbrella).

## Reference index

- `references/lookforge-debug.md` — LookForge Phase2/3/6 backend integration: PhaseOrchestrator, SkillDispatcher, KnowledgeBase hooks, dead code detection, Phase6 hardware workflow.
- `references/lookforge-chromadb-debug.md` — LookForge ChromaDB-specific issues: Docker deployment, volume mounts, version compatibility, Schema migration, healthcheck fixes. **Note**: For generic ChromaDB 0.4.x runtime bugs (numpy 2.x, seq_id BLOB), see `bugfix` umbrella instead.
- `references/fish-sim-debug.md` — 鱼乐宝 `simulation_core.py`: growth calculation, FCR anomalies, feeding anomalies.
- `references/lookforge-knowledge-health.md` — LookForge ChromaDB 知识库健康度监控 (`get_health_score()`, 盲区发现, query_log).

## Recipe format

Each reference follows:
1. **Symptom** — what you observe in production
2. **Diagnostic steps** — how to confirm it's this issue (not something else)
3. **Fix** — code or config change
4. **Verification** — confirm it works

## Adding new entries

When you spend >1 hour debugging a specific 渔芯 product and the fix is non-obvious, add a `references/<project>-<component>-debug.md` file. Don't create a new top-level skill.
