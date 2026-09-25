#!/usr/bin/env python3
"""One-shot R-round entry write — hardened variant (R673, first-try proven 2026-09-22).

Upgrades the R662 original with three disciplines composed in one script:
  1. probe ground-truth assert BEFORE the fixpoint loop (desc drift surfaces
     early, not after write — R432 family);
  2. derived slots @@P@@ (projection) / @@M@@ (margin) resolved inside the
     same fixpoint loop as @@L@@ (R525: derived values must be computed, never
     pre-filled);
  3. R666 fingerprint gate inline before the writer call (CJK fingerprints
     verbatim from the entry body + garbage scan), then R424 four-item check.

Chain: connect -> pre assert -> (optional span probe with R484 pos-0 branch)
-> entry build -> fixpoint -> asserts -> write /tmp -> subprocess
direct_prune_write positional args -> check superset output.

EDIT POINTS: everything between the EDIT-PER-ROUND markers.
Run: python3 this_script.py   (no args)
"""
import re
import sqlite3
import subprocess
import sys

DB = '/Users/hua/.hermes/tasks.db'
TASK_ID = 11
WRITER = '/Users/hua/.hermes/skills/laomo-heartbeat/scripts/direct_prune_write.py'
ENTRY_PATH = '/tmp/lm_oneshot_entry.txt'
GATE = 49152

# ==================== EDIT PER ROUND ====================
NEW_R = 673
PREV_R = 672
PRUNE_N = 1                       # 0 = no prune (projection uses pre+2+len)
CHECK_IDS = [651, 652, 653, 673]  # superset: suspended + this round pruned + NEW_R
SHED = 2228                       # span of oldest entry (--instr-r measured); None = probe below
PRE_EXPECT = 47123                # previous round's probe desc chars (ground truth)
# Fingerprints verbatim from TEMPLATE body; each must appear >= 1 time.
FINGERPRINTS = ['二百三十二犯', '华哥充值账户 2117577211', 'dir1_paper_scan.py --dry-run']
TEMPLATE = """[R673 2026-09-22 08:2x CST laomo] vs R672 +~33min (库锚 UTC ... = CST ... 刷锚正常 ✓)。hourly silent round mini (协议 step 5, R355 抑制段照贴)。

【抑制段 (R355 boilerplate)】…（照贴当轮标准段）…

【投影+drop】pre=@@PRE@@ chars; 本条 len=@@L@@; 无剪投影 = @@PRE@@+2+@@L@@ 必超闸口 → prune @@N@@ 预期; 剪后投影 = @@BASE@@+2+@@L@@ = @@P@@ < 49152 margin @@M@@ 预期 PASS; check = @@CHECK@@。

keep_in_progress。
"""
# ========================================================

NL = chr(10)
db = sqlite3.connect(DB)
desc = db.execute('SELECT description FROM tasks WHERE id=?', (TASK_ID,)).fetchone()[0]
pre = len(desc)
assert pre == PRE_EXPECT, 'desc drifted: %d != %d (re-probe before writing)' % (pre, PRE_EXPECT)


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


if PRUNE_N > 0 and SHED is None:
    oldest = int(re.findall(r'(?m)^\[R(\d+) ', desc)[0])
    SHED = span(oldest)
    assert SHED, 'span probe failed'

base = pre if PRUNE_N == 0 else pre - SHED
shed_note = 0 if PRUNE_N == 0 else SHED


def make(L):
    p = base + 2 + L
    t = (TEMPLATE.replace('@@PRE@@', str(pre))
                 .replace('@@N@@', str(PRUNE_N))
                 .replace('@@BASE@@', str(base))
                 .replace('@@CHECK@@', ' '.join(str(i) for i in CHECK_IDS)))
    return t.replace('@@L@@', str(L)).replace('@@P@@', str(p)).replace('@@M@@', str(GATE - p))


L = len(TEMPLATE)
for _ in range(30):
    t = make(L)
    if len(t) == L:
        break
    L = len(t)
else:
    sys.exit('FATAL: fixpoint not converged')
assert '@@' not in t, 'placeholder residue'

# R424 four-item check
assert t.count('[R%d ' % NEW_R) == 1, 'marker count'
assert t.rstrip().endswith('keep_in_progress。'), 'tail marker'
# R666 fingerprint gate (fingerprints verbatim from TEMPLATE, garbage scan)
for fp in FINGERPRINTS:
    assert t.count(fp) >= 1, 'fingerprint missing: ' + fp
for bad in ['@@', 'PROJ_PLACEHOLDER', 'LENPLACE', 'ARK_RESULT_PLACEHOLDER']:
    assert bad not in t, 'garbage residue: ' + bad

proj = base + 2 + L
assert proj < GATE, 'FATAL: projection over gate: %d' % proj

with open(ENTRY_PATH, 'w', encoding='utf-8') as f:
    f.write(t)

print('entry_len:', L, '| pre:', pre, '| shed:', shed_note, '| proj:', proj, '| margin:', GATE - proj)

cmd = ['python3', WRITER, ENTRY_PATH, str(PRUNE_N)]
cmd += [str(i) for i in CHECK_IDS]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
print(r.stdout[-3000:])
if r.stderr:
    print('STDERR:', r.stderr[-500:])
sys.exit(r.returncode)
