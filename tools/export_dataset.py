"""Xuất toàn bộ dataset ra một file gộp ở các định dạng dùng được ngay.

Sinh ra trong `datasets/exports/`:

* `dra_queries_all.csv`   -- mở bằng Excel/pandas/R.
* `dra_queries_all.jsonl` -- một bản ghi mỗi dòng, tiện cho pipeline streaming.

Chạy: `python tools/export_dataset.py`
      `python tools/export_dataset.py --check`
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dra_utils import (  # noqa: E402
    EXPORTS_DIR,
    LABEL_NAMES,
    load_all,
    setup_stdout,
    tokenize,
    write_text,
)

FIELDS = ("id", "query", "domain", "label", "label_name", "n_tokens", "source")


def rows() -> List[Dict[str, object]]:
    exported = []
    for record in sorted(load_all(), key=lambda item: (str(item["source"]), str(item["id"]))):
        label = int(record["label"])
        exported.append({
            "id": record["id"],
            "query": record["query"],
            "domain": record["domain"],
            "label": label,
            "label_name": LABEL_NAMES.get(label, "unknown"),
            "n_tokens": len(tokenize(str(record["query"]))),
            "source": record["source"],
        })
    return exported


def to_csv(exported: List[Dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(exported)
    return buffer.getvalue()


def to_jsonl(exported: List[Dict[str, object]]) -> str:
    return "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in exported)


def main() -> int:
    setup_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="thoát với mã 1 nếu file xuất đã lỗi thời")
    args = parser.parse_args()

    exported = rows()
    outputs = {
        EXPORTS_DIR / "dra_queries_all.csv": to_csv(exported),
        EXPORTS_DIR / "dra_queries_all.jsonl": to_jsonl(exported),
    }

    if args.check:
        stale = [path for path, content in outputs.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            names = ", ".join(path.name for path in stale)
            print(f"File xuất đã lỗi thời ({names}). Chạy: python tools/export_dataset.py",
                  file=sys.stderr)
            return 1
        print("File xuất đã cập nhật.")
        return 0

    for path, content in outputs.items():
        write_text(path, content)
        print(f"Đã ghi {path} ({len(exported)} bản ghi)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
