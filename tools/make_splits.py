"""Sinh split train/dev/test phân tầng, tái lập được, cho bài toán định tuyến.

Phân tầng theo cặp `(domain, label)` để mọi split giữ nguyên tỉ lệ miền và tỉ lệ
nhãn của dữ liệu gốc. Thứ tự bản ghi được sắp theo `id` trước khi trộn nên kết
quả chỉ phụ thuộc vào seed, không phụ thuộc thứ tự file trên đĩa.

Chạy: `python tools/make_splits.py`         -> ghi datasets/splits/
      `python tools/make_splits.py --check` -> xác nhận split trên đĩa khớp seed
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dra_utils import (  # noqa: E402
    SPLITS_DIR,
    group_by,
    load_all,
    setup_stdout,
    write_json,
)

DEFAULT_SEED = 20260819
DEFAULT_RATIOS = (0.70, 0.15, 0.15)
SPLIT_NAMES = ("train", "dev", "test")


def stratified_split(records: Sequence[Dict[str, object]], seed: int,
                     ratios: Tuple[float, float, float]) -> Dict[str, List[Dict[str, object]]]:
    """Chia bản ghi thành train/dev/test, phân tầng theo `(domain, label)`."""

    if abs(sum(ratios) - 1.0) > 1e-9:
        raise ValueError(f"tổng tỉ lệ phải bằng 1.0, nhận {sum(ratios)}")

    splits: Dict[str, List[Dict[str, object]]] = {name: [] for name in SPLIT_NAMES}
    strata = group_by(records, "__stratum__")

    for key in sorted(strata, key=str):
        bucket = sorted(strata[key], key=lambda record: str(record["id"]))
        random.Random(f"{seed}:{key}").shuffle(bucket)

        total = len(bucket)
        n_train = round(total * ratios[0])
        n_dev = round(total * (ratios[0] + ratios[1])) - n_train
        splits["train"] += bucket[:n_train]
        splits["dev"] += bucket[n_train:n_train + n_dev]
        splits["test"] += bucket[n_train + n_dev:]

    for name in SPLIT_NAMES:
        splits[name].sort(key=lambda record: str(record["id"]))
    return splits


def prepare(records: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    """Gắn khoá phân tầng và giữ thứ tự trường ổn định."""

    prepared = []
    for record in records:
        prepared.append({
            "id": record["id"],
            "query": record["query"],
            "domain": record["domain"],
            "label": int(record["label"]),
            "source": record["source"],
            "__stratum__": f"{record['domain']}|{record['label']}",
        })
    return prepared


def strip_stratum(records: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    return [{key: value for key, value in record.items() if key != "__stratum__"}
            for record in records]


def build(seed: int, ratios: Tuple[float, float, float]) -> Tuple[Dict[str, List[Dict[str, object]]], Dict[str, object]]:
    records = prepare(load_all())
    splits = {name: strip_stratum(bucket)
              for name, bucket in stratified_split(records, seed, ratios).items()}

    manifest: Dict[str, object] = {
        "seed": seed,
        "ratios": {name: ratio for name, ratio in zip(SPLIT_NAMES, ratios)},
        "stratified_by": ["domain", "label"],
        "generator": "tools/make_splits.py",
        "total_records": len(records),
        "splits": {},
    }
    for name in SPLIT_NAMES:
        bucket = splits[name]
        manifest["splits"][name] = {
            "file": f"{name}.json",
            "count": len(bucket),
            "labels": dict(sorted(Counter(record["label"] for record in bucket).items())),
            "domains": dict(sorted(Counter(record["domain"] for record in bucket).items())),
        }
    return splits, manifest


def files_match(splits: Dict[str, List[Dict[str, object]]], manifest: Dict[str, object]) -> bool:
    expected = {f"{name}.json": splits[name] for name in SPLIT_NAMES}
    expected["manifest.json"] = manifest
    for filename, data in expected.items():
        path = SPLITS_DIR / filename
        if not path.exists():
            return False
        if json.loads(path.read_text(encoding="utf-8")) != json.loads(
                json.dumps(data, ensure_ascii=False)):
            return False
    return True


def main() -> int:
    setup_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"mặc định {DEFAULT_SEED}")
    parser.add_argument("--ratios", type=float, nargs=3, default=list(DEFAULT_RATIOS),
                        metavar=("TRAIN", "DEV", "TEST"), help="tỉ lệ train/dev/test, tổng = 1.0")
    parser.add_argument("--check", action="store_true",
                        help="thoát với mã 1 nếu datasets/splits/ không khớp seed hiện tại")
    args = parser.parse_args()

    splits, manifest = build(args.seed, tuple(args.ratios))

    if args.check:
        if not files_match(splits, manifest):
            print("datasets/splits/ không khớp seed hiện tại. Chạy: python tools/make_splits.py",
                  file=sys.stderr)
            return 1
        print("datasets/splits/ khớp với seed hiện tại.")
        return 0

    for name in SPLIT_NAMES:
        write_json(SPLITS_DIR / f"{name}.json", splits[name])
    write_json(SPLITS_DIR / "manifest.json", manifest)

    print(f"Đã ghi split vào {SPLITS_DIR} (seed={args.seed})")
    for name in SPLIT_NAMES:
        info = manifest["splits"][name]
        print(f"  {name:5s}: {info['count']:4d} bản ghi, nhãn {info['labels']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
