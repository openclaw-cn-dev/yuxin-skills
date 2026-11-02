#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""玉芬管理进化扫描: skill 容量 + agent 心跳 (2026-10-06)"""
import os, datetime

NOWDT = datetime.datetime.now()
OUT = []
P = OUT.append

# ============ skill capacity ============
P("### SKILL CAPACITY ###")
def scan_skills(root):
    n_files = 0
    n_chars = 0
    big = []  # (chars, path)
    for root2, dirs, files in os.walk(root):
        # skip archive dirs
        dirs[:] = [d for d in dirs if d not in (".archive", "archive", "__pycache__")]
        for f in files:
            if f == "SKILL.md":
                fp = os.path.join(root2, f)
                try:
                    c = os.path.getsize(fp)
                    n_files += 1
                    n_chars += c
                    if c > 100 * 1024:
                        big.append((c, fp))
                except Exception:
                    pass
    return n_files, n_chars, sorted(big, reverse=True)

roots = [("/Users/hua/.hermes/skills", "global-root")]
for pj in sorted(os.listdir("/Users/hua/.hermes/profiles")):
    sp = "/Users/hua/.hermes/profiles/%s/skills" % pj
    if os.path.isdir(sp):
        roots.append((sp, pj))

tot_f, tot_c = 0, 0
for root, label in roots:
    f, c, big = scan_skills(root)
    tot_f += f
    tot_c += c
    P("SKILL %-12s files=%d chars=%d (%.1fM)" % (label, f, c, c / 1048576.0))
    for bc, bp in big[:3]:
        P("  BIG %.0fK %s" % (bc / 1024, bp.replace("/Users/hua/.hermes/profiles/", "")))
P("SKILL TOTAL files=%d chars=%.1fM" % (tot_f, tot_c / 1048576.0))

# archived
arch_n = 0
arch_c = 0
ap = "/Users/hua/.hermes/skills/.archive"
if os.path.isdir(ap):
    for root2, dirs, files in os.walk(ap):
        for f in files:
            if f == "SKILL.md":
                arch_n += 1
                arch_c += os.path.getsize(os.path.join(root2, f))
P("SKILL global-archive files=%d chars=%.1fM" % (arch_n, arch_c / 1048576.0))

# ============ agent heartbeat ============
P("### AGENT HEARTBEAT ###")
profiles_base = "/Users/hua/.hermes/profiles"
for prof in sorted(os.listdir(profiles_base)):
    pdir = os.path.join(profiles_base, prof)
    if not os.path.isdir(pdir):
        continue
    latest = 0
    latest_path = ""
    for root2, dirs, files in os.walk(pdir):
        dirs[:] = [d for d in dirs if d not in ("skills", "node_modules", "__pycache__")]
        for f in files:
            fp = os.path.join(root2, f)
            try:
                mt = os.path.getmtime(fp)
                if mt > latest:
                    latest = mt
                    latest_path = fp.replace(pdir, "")
            except Exception:
                pass
    if latest:
        dt = datetime.datetime.fromtimestamp(latest)
        days = (NOWDT - dt).total_seconds() / 86400
        P("AGENT %-12s last=%s (%.1fd) %s" % (prof, dt.strftime("%m-%d %H:%M"), days, latest_path[:50]))
    else:
        P("AGENT %-12s EMPTY" % prof)

print("\n".join(OUT))
