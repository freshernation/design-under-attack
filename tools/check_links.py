#!/usr/bin/env python3
"""Every relative link inside content/ must resolve.

The articles are written to be publishable as standalone pages, which only stays
true if the tree is internally consistent.

    python3 tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

# [text](target) — target captured up to the closing paren or a title string
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)")


def main() -> int:
    broken: list[str] = []
    checked = 0

    for path in sorted(CONTENT.rglob("*.md")):
        for target in LINK.findall(path.read_text()):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            checked += 1
            resolved = (path.parent / target.split("#")[0]).resolve()
            if not resolved.exists():
                broken.append(f"{path.relative_to(ROOT)} -> {target}")

    if broken:
        print(f"{len(broken)} broken relative link(s):\n")
        for item in broken:
            print(f"  {item}")
        return 1

    print(f"OK — {checked} relative link(s) resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
