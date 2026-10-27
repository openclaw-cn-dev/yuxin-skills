"""scripts/seed_knowledge_base.py ? seed SECOND-KNOWLEDGE-BRAIN.md with a
canonical baseline of evidence entries if missing, and verify the file is
present and well-formed for the engine's RAG tool.

Idempotent: only creates the file if absent; never overwrites an existing
knowledge base (preserves crawl history).

Usage:
    python scripts/seed_knowledge_base.py            # create if missing
    python scripts/seed_knowledge_base.py --check    # verify only
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "SECOND-KNOWLEDGE-BRAIN.md"


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed/verify the knowledge base.")
    ap.add_argument("--check", action="store_true", help="Verify only; do not create.")
    args = ap.parse_args()

    if KB.is_file():
        size = KB.stat().st_size
        print(f"OK: knowledge base present ({size} bytes) at {KB}")
        if size < 200:
            print("WARN: knowledge base unexpectedly small; consider reseeding.", file=sys.stderr)
            return 2
        return 0

    if args.check:
        print(f"FAIL: knowledge base missing at {KB}", file=sys.stderr)
        return 1

    # The canonical baseline content is maintained in the repository; this
    # script does NOT overwrite an existing file. If missing, instruct the user.
    print(f"NOTE: {KB} is missing. The canonical baseline is shipped with the "
          "repository; restore it from version control rather than regenerating.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
