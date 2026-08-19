"""Kiểm định các file trong `datasets/` theo schema và quy ước của dự án.

Chạy: `python tools/validate_datasets.py [--strict]`

Thoát với mã 1 nếu có lỗi (ERROR). Với `--strict`, cảnh báo (WARN) cũng bị coi
là lỗi -- dùng cho CI khi muốn siết chặt.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dra_utils import (  # noqa: E402
    DOMAIN_BY_SLUG,
    REQUIRED_FIELDS,
    VALID_LABELS,
    dataset_paths,
    normalize_query,
    setup_stdout,
    slug_of,
)

CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
REPLACEMENT_CHAR = "�"


class Report:
    """Thu thập lỗi và cảnh báo trong quá trình kiểm định."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")


def check_record(report: Report, where: str, record: object) -> None:
    if not isinstance(record, dict):
        report.error(where, f"bản ghi phải là object, nhận {type(record).__name__}")
        return

    extra = sorted(set(record) - set(REQUIRED_FIELDS))
    missing = sorted(set(REQUIRED_FIELDS) - set(record))
    if missing:
        report.error(where, f"thiếu trường {missing}")
    if extra:
        report.warn(where, f"có trường ngoài schema {extra}")

    query = record.get("query")
    if isinstance(query, str):
        if not query.strip():
            report.error(where, "`query` rỗng")
        elif query != query.strip():
            report.warn(where, "`query` có khoảng trắng thừa ở đầu/cuối")
        if CONTROL_RE.search(query):
            report.error(where, "`query` chứa ký tự điều khiển")
        if REPLACEMENT_CHAR in query:
            report.error(where, "`query` chứa U+FFFD (dấu hiệu hỏng mã hoá)")
        if query != unicodedata.normalize("NFC", query):
            report.warn(where, "`query` chưa ở dạng chuẩn hoá NFC")
        if len(query) < 10:
            report.warn(where, f"`query` rất ngắn ({len(query)} ký tự)")
    elif "query" in record:
        report.error(where, f"`query` phải là chuỗi, nhận {type(query).__name__}")

    domain = record.get("domain")
    if "domain" in record and (not isinstance(domain, str) or not domain.strip()):
        report.error(where, "`domain` phải là chuỗi không rỗng")

    label = record.get("label")
    if "label" in record:
        if isinstance(label, bool) or not isinstance(label, int):
            report.error(where, f"`label` phải là số nguyên, nhận {type(label).__name__}")
        elif label not in VALID_LABELS:
            report.error(where, f"`label` phải thuộc {list(VALID_LABELS)}, nhận {label}")


def validate_file(report: Report, path: Path) -> List[Dict[str, object]]:
    name = path.name
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        report.error(name, f"không đọc được bằng UTF-8: {exc}")
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        report.error(name, f"JSON không hợp lệ (dòng {exc.lineno}, cột {exc.colno}): {exc.msg}")
        return []

    if not isinstance(data, list):
        report.error(name, f"file phải chứa một mảng, nhận {type(data).__name__}")
        return []
    if not data:
        report.error(name, "file không có bản ghi nào")
        return []

    for index, record in enumerate(data):
        check_record(report, f"{name}[{index}]", record)

    records = [record for record in data if isinstance(record, dict)]

    slug = slug_of(path)
    expected_domain = DOMAIN_BY_SLUG.get(slug)
    domains = Counter(str(record.get("domain")) for record in records)
    if expected_domain is None:
        report.warn(name, f"slug `{slug}` chưa khai báo trong DOMAIN_BY_SLUG (tools/dra_utils.py)")
    elif set(domains) != {expected_domain}:
        report.error(name, f"`domain` phải luôn là '{expected_domain}', thực tế {dict(domains)}")

    labels = Counter(record.get("label") for record in records)
    zeros, ones = labels.get(0, 0), labels.get(1, 0)
    if zeros and ones:
        skew = abs(zeros - ones) / (zeros + ones)
        if skew > 0.1:
            report.warn(name, f"nhãn lệch {skew:.0%} (0: {zeros}, 1: {ones})")

    seen: Dict[str, int] = {}
    for index, record in enumerate(records):
        query = record.get("query")
        if not isinstance(query, str):
            continue
        key = normalize_query(query)
        if key in seen:
            report.error(name, f"truy vấn trùng lặp tại [{index}] và [{seen[key]}]: {query[:70]!r}")
        else:
            seen[key] = index

    print(f"  {name}: {len(records)} bản ghi, nhãn 0={zeros} / 1={ones}")
    return records


def check_cross_file(report: Report, by_file: Dict[str, List[Dict[str, object]]]) -> None:
    """Phát hiện truy vấn trùng lặp giữa các file khác nhau."""

    index: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for name, records in by_file.items():
        for record in records:
            query = record.get("query")
            if isinstance(query, str):
                index[normalize_query(query)].append((name, query))

    for occurrences in index.values():
        files = {name for name, _ in occurrences}
        if len(files) > 1:
            report.error(
                "cross-file",
                f"truy vấn xuất hiện ở nhiều file {sorted(files)}: {occurrences[0][1][:70]!r}",
            )


def main() -> int:
    setup_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="coi cảnh báo là lỗi")
    args = parser.parse_args()

    paths = dataset_paths()
    if not paths:
        print("Không tìm thấy file nào khớp datasets/dataset_*.json", file=sys.stderr)
        return 1

    report = Report()
    print(f"Kiểm định {len(paths)} file dataset:")
    by_file = {path.name: validate_file(report, path) for path in paths}
    check_cross_file(report, by_file)

    for warning in report.warnings:
        print(f"WARN  {warning}")
    for error in report.errors:
        print(f"ERROR {error}", file=sys.stderr)

    total = sum(len(records) for records in by_file.values())
    print(f"\nTổng: {total} bản ghi, {len(report.errors)} lỗi, {len(report.warnings)} cảnh báo.")

    if report.errors:
        return 1
    if args.strict and report.warnings:
        print("Chế độ --strict: cảnh báo được tính là lỗi.", file=sys.stderr)
        return 1
    print("Tất cả kiểm định đã qua.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
