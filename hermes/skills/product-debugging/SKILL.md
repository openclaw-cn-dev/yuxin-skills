---
name: product-debugging
description: "Product-specific debugging playbooks — issue triage and root-cause analysis for 渔芯 (Yuxin) products including Fish Sim, LookForge, and ChromaDB integrations."
version: 1.0.0
author: 渔芯科技
platforms: [linux, macos]
metadata:
  hermes:
    tags: [debugging, yuxin, fish-sim, lookforge, chromadb, triage, root-cause]
---

# Product Debugging

Issue triage and root-cause analysis playbooks for 渔芯 products.

## When to Use

- 鱼乐宝 (Fish Sim) simulation results unexpected — growth, FCR, feeding anomalies
- LookForge PhaseOrchestrator/SkillDispatcher/KnowledgeBase integration issues
- LookForge ChromaDB Docker deployment, version compatibility, or data sync problems

## Fish Sim (鱼乐宝) — simulation_core.py

### Quick Verification

Validate growth calculations, FCR, and health across all three fish species:

```bash
cd /Users/hua/Desktop/渔芯科技/6-产品研发/01-鱼乐宝/backend
python3 -c "
import sys; sys.path.insert(0, '.')
import warnings; warnings.filterwarnings('ignore')
from app.api.v1.simulation_core import SimSession, CreateSessionRequest

configs = [
    ('F001', 1.0, 25.0, 60, 1000),
    ('F003', 10.0, 500.0, 90, 1000),
    ('F005', 50.0, 1500.0, 180, 500),
]
for fid, iw, tw, days, fc in configs:
    req = CreateSessionRequest(fish_id=fid, fish_count=fc, init_weight=iw,
        target_weight=tw, total_days=days, tank_volume=100.0,
        feed_price=15.0, fish_price=50.0)
    s = SimSession(req)
    s.step(hours=days*24)
    r = s.generate_report()
    status = 'PASS' if r['growth_achieved'] >= 0.80 else 'FAIL'
    print(f'{fid} {iw}g->{r[\"final_weight\"]:.1f}g (target {tw}g) [{status}] '
          f'FCR={r[\"FCR\"]} Health={r[\"final_health\"]:.2f} '
          f'Survival={r[\"avg_survival\"]*100:.1f}%')
"
```

**Acceptance criteria:** 3/3 PASS, FCR 0.2–1.5, health ≥ 0.3.

### Key Files

| File | Role |
|------|------|
| `app/api/v1/simulation_core.py` | Core simulation engine |
| `app/models/fish_profile.py` | Fish species growth curves + parameters |
| `app/models/feeding.py` | Feeding rate calculations |

### Common Issues

- **FCR anomalies** → check temperature curve alignment with feeding rate formula
- **Health drops too fast** → verify oxygen demand calculation in `_update_water_quality()`
- **Growth too slow/fast** → check species-specific growth curve parameters in `fish_profile.py`
- **Negative values** → overflow in accumulated metrics, check `int` → `float` conversions

## LookForge — PhaseOrchestrator / SkillDispatcher

### Core Diagnostic Checklist

1. **SkillDispatcher knowledge injection** — check `_build_prompt()` for ChromaDB query:
   ```python
   knowledge_context = self._retrieve_knowledge(skill_name, context)
   ```
   If only project/profile/research_report are present → knowledge disconnected.

2. **`generate_development_details()` dead code** — outputs generic templates ("简约现代/科技硬核/可爱亲和") not extracted from `research_report.competitors[].features`.

3. **PhaseOrchestrator ChromaDB call chain** — trace: `run_phase2()` → `_build_prompt()` → `_retrieve_knowledge()` → ChromaDB `.query()`.

### Verification

```bash
cd /Users/hua/Desktop/渔芯科技/LookForge
# Check if knowledge base is reachable
python3 -c "from app.services.knowledge_base import KnowledgeBase; kb = KnowledgeBase(); print(kb.collection.count())"
# Expected: > 0 documents
```

## LookForge — ChromaDB Docker Debug

Full debugging playbook for LookForge's ChromaDB Docker deployment. See `references/lookforge-chromadb.md` for the complete reference covering:

- Architecture (containers + shared volume)
- Common failure patterns (NumPy/onnxruntime incompatibility, version pinning)
- Health check restoration recipe
- Schema migration (0.4.x → 0.6.x)
- Volume mount verification
- Snapshot backup/restore
- Docker Compose configuration reference
