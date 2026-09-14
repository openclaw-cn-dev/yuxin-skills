#!/usr/bin/env python3
"""Insert one defense-wall line into the laomo-heartbeat SKILL.md wall segment.

Packaged consolidation of the R433/R453/R454/R456 rules (R462 hand-written
version passed first try, then frozen as this tool):
  - MARK derived same-source from the wall-line file head (no hand-typed
    codepoints -> R438/R450/R453 codepoint-transposition family immune)
  - idempotent guard: skip if MARK already present (R433)
  - insert before FIRST occurrence of the anchor (R456: anchor phrase may be
    referenced elsewhere, first occurrence is the wall segment, R370)
  - landing check: MARK count==1 AND pos(MARK) < pos(anchor) with bounded
    distance (R454/R456: pre-capture anchor pos, '<' only for inserted-newline
    adjacency, no rfind)
Usage:
    python3 wall_line_insert.py <wall_line_file> [skill_md_path]
Wall-line file: one line starting with 'R<digits> ' (CJK allowed inside).
Skill path defaults to the L1 laomo-heartbeat SKILL.md.
"""
import io
import re
import sys

DEFAULT_SKILL = "/Users/hua/.hermes/skills/laomo-heartbeat/SKILL.md"
# anchor built via chr() (R438/R442: chr() construction stable across both
# authoring channels; long \uXXXX escapes break under write_file)
ANCHOR = (
    chr(0x82E5) + chr(0x786E) + chr(0x9700) + chr(0x5B9A) + chr(0x4F4D)
)  # = "ruo que xu ding wei" (locate-if-needed phrase)


def main():
    if len(sys.argv) < 2:
        print("usage: wall_line_insert.py <wall_line_file> [skill_md_path]")
        return 2
    wall_path = sys.argv[1]
    skill_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SKILL

    with io.open(wall_path, encoding="utf-8") as f:
        line = f.read().strip()
    if not line:
        print("FATAL: wall-line file empty")
        return 1
    tok = line.split()[0]
    if not re.match(r"^R\d+$", tok):
        print("FATAL: wall line must start with 'R<digits> ', got: %r" % tok)
        return 1

    with io.open(skill_path, encoding="utf-8") as f:
        s = f.read()

    mark = "\n" + tok + " "
    newline = "\n" + line
    apos = s.find(ANCHOR)
    if apos < 0:
        print("FATAL: anchor not found in skill file")
        return 1

    if s.count(mark) > 0:
        print("ALREADY_PRESENT count=%d -- skip (idempotent guard)" % s.count(mark))
        return 0

    s2 = s[:apos] + newline + " " + s[apos:]

    p = s2.find(mark)
    q = s2.find(ANCHOR)
    if s2.count(mark) != 1 or not (p < q and q - p < len(newline) + 4):
        print(
            "FATAL: landing check failed (count=%d p=%d q=%d) -- file NOT written"
            % (s2.count(mark), p, q)
        )
        return 1

    with io.open(skill_path, "w", encoding="utf-8") as f:
        f.write(s2)

    with io.open(skill_path, encoding="utf-8") as f:
        s3 = f.read()
    ok = s3.count(mark) == 1 and s3.find(mark) < s3.find(ANCHOR)
    if ok:
        print("WALL_INSERT_OK count=1 pos<anchor verified")
        return 0
    print("FATAL: post-write verify failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
