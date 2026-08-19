"""Trich phan ghi chu cua mot phien ban tu CHANGELOG.md.

Dung trong workflow Release:
    python .github/scripts/extract_release_notes.py v1.1.0 release_notes.md

Neu khong tim thay muc tuong ung, ghi ra mot ghi chu chung thay vi that bai --
phat hanh khong nen bi chan chi vi CHANGELOG chua kip cap nhat.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHANGELOG = REPO_ROOT / "CHANGELOG.md"


def extract(tag: str, text: str) -> str:
    version = tag.lstrip("vV")
    pattern = rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return f"Xem CHANGELOG.md de biet thay doi cua phien ban {version}."


def main(argv: list) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2

    tag, output = argv[1], argv[2]
    text = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""
    notes = extract(tag, text)

    Path(output).write_text(notes + "\n", encoding="utf-8", newline="\n")
    print(f"Da ghi ghi chu phat hanh cho {tag} vao {output} ({len(notes)} ky tu)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
