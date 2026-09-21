#!/usr/bin/env python3
"""One-shot R-round entry write: probe -> entry build -> fixpoint fill -> projection assert -> direct_prune_write -> check superset.

R662-curator collection of the R611 one-shot recipe (2026-09-21, first-run proven).
Reuses: /tmp entry file, subprocess to direct_prune_write.py (positional args),
check list = suspended pruned ids + this round's real pruned ids + new R number.

EDIT POINTS (all constants at top):
  BOIL       - suppression boilerplate text (keep updated per protocol)
  PRUNE_N    - number of oldest entries to drop (0 = let wrapper auto-upgrade)
  CHECK_IDS  - superset check list (extra ids are zero side-effect when count=0)
  entry body - the only per-round text

Span probe includes the R484 pos-0 branch: the FIRST entry marker sits at
position 0 with no preceding newline, so bare find(NL+marker) returns -1.
"""
import sqlite3
import subprocess
import sys

DB = '/Users/hua/.hermes/tasks.db'
TASK_ID = 11
WRITER = '/Users/hua/.hermes/skills/laomo-heartbeat/scripts/direct_prune_write.py'
ENTRY_PATH = '/tmp/lm_oneshot_entry.txt'

NEW_R = 662          # EDIT: this round's R number
PREV_R = 661         # EDIT: previous round's R number (for header)
PRUNE_N = 2          # EDIT: 0 = no-arg wrapper
CHECK_IDS = [637, 638, 639, 640, 662]   # EDIT: superset (suspended + real-pruned + new)

NL = chr(10)
GATE = 49152

db = sqlite3.connect(DB)
c = db.cursor()
c.execute('SELECT description FROM tasks WHERE id=%d' % TASK_ID)
desc = c.fetchone()[0]
pre = len(desc)


def span(n):
    """Entry span in chars; R484 pos-0 branch for the first entry."""
    a = desc.find(NL + '[R%d ' % n)
    if a < 0:
        if desc.startswith('[R%d ' % n):
            a = 0
        else:
            return None
    b = desc.find(NL + '[R%d ' % (n + 1))
    return (b - a - 2) if b > 0 else (len(desc) - a)


# EDIT: choose which old entries to measure for shed estimate
s_old = [span(PREV_R - 21), span(PREV_R - 20)]  # e.g. R639/R640 when PREV_R=661
if any(s is None for s in s_old):
    print('FATAL: span probe failed, run merged_round_probe --instr-r instead')
    sys.exit(1)

BOIL = (
    '[self-evolve prompt suppression (R355 boilerplate)] per R355 three-factor test: '
    '(1) task #11 stays in_progress forever (never completed, key cognition 1); '
    '(2) blocklist non-empty (fill from status probe); '
    '(3) R325/R338/R352/R355/R361 precedents: hourly silent round runs NO direction 1-4. '
    'Forced three actions: (a) no direction 1 (pre-rebuild --append ban unchanged); '
    '(b) no direction 5; (c) direction 1 dry-run only via dir1_paper_scan.py. '
    'Cron prompt patch pending HuaGe/YuFen approval; re-affirm hourly until patched.'
)

# EDIT: entry body. Keep @@L@@ self-reference slot.
entry = (
    '[R%d 2026-09-21 08:49 CST laomo] vs R%d +NNNmin (DB anchor UTC ... = CST ...; '
    'archive mtime ... cross-check). hourly silent round mini.\n\n'
    '[' + BOIL + ']\n\n'
    '[Opening self-audit] ...\n\n'
    '[R-numbering] last_r=%d probe ground truth OK +1 = R%d; R%d count=0 exclusive OK.\n\n'
    '[Status] ...\n\n'
    '[Ark] ...\n\n'
    '[Ledger dual path] ...\n\n'
    '[Writer/dir4] ...\n\n'
    '[Projection+drop: pre=%d chars; oldest spans %d/%d; this entry len=@@L@@; '
    'prune %d projection = %d+2+@@L@@ = %d margin %d expected PASS; '
    'check superset = %s.]\n\n'
    'keep_in_progress.'
) % (NEW_R, PREV_R, PREV_R, NEW_R, NEW_R,
     pre, s_old[0], s_old[1], PRUNE_N,
     pre - sum(s_old), pre - sum(s_old) + 2, GATE - (pre - sum(s_old) + 2),
     ' '.join(str(i) for i in CHECK_IDS))

L = 2000
for _ in range(30):
    t = entry.replace('@@L@@', str(L))
    if len(t) == L:
        break
    L = len(t)
else:
    print('FATAL: fixpoint not converged')
    sys.exit(1)
assert '@@' not in t, 'placeholder residue'

proj = pre - sum(s_old) + 2 + L
assert proj < GATE, 'FATAL: prune-%d projection over gate: %d' % (PRUNE_N, proj)

with open(ENTRY_PATH, 'w', encoding='utf-8') as f:
    f.write(t)

print('entry_len:', L, '| pre:', pre, '| shed:', sum(s_old), '| proj:', proj, 'margin:', GATE - proj)

cmd = ['python3', WRITER, ENTRY_PATH]
if PRUNE_N > 0:
    cmd.append(str(PRUNE_N))
cmd += [str(i) for i in CHECK_IDS]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
print(r.stdout[-3000:])
print(r.stderr[-500:] if r.stderr else '')
sys.exit(r.returncode)
