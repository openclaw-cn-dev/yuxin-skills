# 0910 cron iron rules - cross-day data drift + SKILL.md live validation

> 0910 cron 9:00 live verification. 3 new iron rules. SKILL.md top-priority read.

## Symptom

0910 cron started with cross-session memory saying SKILL.md 146KB > 100K limit, needs split. But live check: SKILL.md = 6,014 bytes / 113 lines — already split by 0909 cron (24h earlier) into references/full-skill-archive.md (145KB / 2,348 lines).

If blindly following memory and running tail -n +1122 to references/changelog-and-templates.md, would have created 0-byte empty file polluting references/, plus false report of "just split".

Same time: AGENTS.md 0909 cron wrote "7 enabled curated plugins + model gpt-5.6-sol". 0910 live = 10 enabled + gpt-5.6-terra. Copying yesterday numbers would propagate drift.

## 3 new iron rules

### Rule 1: mutable state must be live-checked, never trusted from memory

Scope: SKILL.md size, plugin enabled count, model config, fs skill count, sibling cron remote SHA — all daily-mutable, memory version may be N days stale.

- YES: cron step 1 must run wc -c SKILL.md + codex plugin list grep count + cat config.toml grep model + ls skills count + git log origin/main -1
- YES: memory / AGENTS.md numbers are "yesterday snapshot" only, live check before any action
- NO: do not act on memory saying "X state wrong" without verifying (0910 nearly re-split SKILL.md)
- NO: do not freeze AGENTS.md at "7 enabled" forever (0920 may be 10)

Anti-example (0910 almost happened):

```bash
# memory hint: SKILL.md 146KB, need split
# correct action:
wc -c SKILL.md
# 6014 SKILL.md  <- already split, 0 action

# wrong action:
tail -n +1122 SKILL.md > references/changelog-and-templates.md
# <- 0-byte empty file, pollutes references/, false split report
```

### Rule 2: plugin count + model name live-calc every cron, never copy yesterday

0909 report drift cases:

- openai-curated-remote enabled: 0909 said 7, 0910 live = 10 (extra: google-drive / canva / apollo / plugin-management / sales / product-design / creative-production / app-69xxx / openai-templates / deep-research-work)
- model: 0909 said gpt-5.6-sol, 0910 live = gpt-5.6-terra (config.toml model_reasoning_effort low)

- YES: daily cron must run: codex plugin list grep installed-enabled wc -l, and grep model config.toml
- YES: report "X plugins" must segment by marketplace (bundled X / primary-runtime X / curated-remote X), not just total
- NO: do not write "19 plugins unchanged" in one line (any segment change total drift)
- NO: do not use yesterday model name (OpenAI backend model name rotates by date)

### Rule 3: split validation = real patch test, not just wc -c

After splitting SKILL.md, beyond wc -c < 10KB, also run a real patch_file write to verify the patch tool no longer rejects.

- YES: SKILL.md self-check 2-step = wc -c (< 10KB) + real patch once (success = split truly done)
- YES: after split, immediately update references index in SKILL.md (do not forget the pointer)
- NO: do not stop at wc (0909 cron pre-split may have missed references pointer)

## 0910 live reconciliation table

| item | 0909 reported | 0910 live | delta |
|---|---|---|---|
| SKILL.md size | 146KB | 6KB | already split (0909 cron) |
| full-skill-archive.md | absent | 145KB / 2,348 lines | created |
| openai-curated-remote enabled | 7 | 10 | +3 |
| model | gpt-5.6-sol | gpt-5.6-terra | model name drift |
| total enabled plugins | 19 | 22 | +3 |
| DEV/MKT/OTHER breakdown | 33/48/30 | 33/48/30 | 0 drift |
| fs real skill count | 111 | 111 | 0-install day 0 drift |
| references reverse scan | 2 false-positive | 2 false-positive | 0 real missing |

## 0910 cron report fix actions

1. AGENTS.md Codex-version section: model field gpt-5.6-sol → gpt-5.6-terra
2. AGENTS.md installed-plugins section: 19 → 22, segmented detail (bundled 7 / primary-runtime 5 / curated-remote 10)
3. AGENTS.md today-changes (2026-09-10) section: 8 new records added
4. references/full-skill-archive.md: kept (0909 cron built it, do not touch)
5. Desktop report codex_evolution_0910.md: 5,240 bytes written (full reconciliation)

## 0910 NO-action list (rule 1 life-saver)

- NO: do not re-split SKILL.md (already 6KB, would break working state)
- NO: do not write references/changelog-and-templates.md (would pollute 27-file references/ list)
- NO: do not copy AGENTS.md 0909 numbers (would freeze 19-miscount)
- NO: do not install new skill (0-install day + sibling silent + 4 business lines fully covered)
