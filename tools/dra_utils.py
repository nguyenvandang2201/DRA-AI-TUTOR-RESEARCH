"""Tiện ích dùng chung cho các script trong `tools/`.

Chỉ dùng thư viện chuẩn của Python (>= 3.9) để mọi script chạy được ngay,
không cần cài đặt thêm gói nào.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = REPO_ROOT / "datasets"
CORPUS_DIR = REPO_ROOT / "corpus"
DOCS_DIR = REPO_ROOT / "docs"
SPLITS_DIR = DATASETS_DIR / "splits"
EXPORTS_DIR = DATASETS_DIR / "exports"

REQUIRED_FIELDS = ("query", "domain", "label")
VALID_LABELS = (0, 1)

LABEL_NAMES = {
    0: "factual",
    1: "analytical",
}

#: Ánh xạ tên file (không có tiền tố `dataset_`) sang giá trị `domain` mong đợi.
DOMAIN_BY_SLUG = {
    "introductory_statistics": "Introductory Statistics",
    "microeconomics": "Microeconomics",
    "world_history": "World History",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def setup_stdout() -> None:
    """Ép stdout/stderr sang UTF-8.

    Console Windows mặc định dùng cp1252 và sẽ vỡ khi in ký tự như ``μ`` hoặc
    ``σ`` vốn xuất hiện trong bộ dữ liệu Thống kê nhập môn.
    """

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def dataset_paths() -> List[Path]:
    """Trả về danh sách file dataset đã sắp xếp theo tên."""

    return sorted(DATASETS_DIR.glob("dataset_*.json"))


def slug_of(path: Path) -> str:
    """`datasets/dataset_world_history.json` -> `world_history`."""

    return path.stem[len("dataset_") :] if path.stem.startswith("dataset_") else path.stem


def load_dataset(path: Path) -> List[Dict[str, object]]:
    """Đọc một file dataset JSON và trả về danh sách bản ghi."""

    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_all(paths: Sequence[Path] | None = None) -> List[Dict[str, object]]:
    """Gộp toàn bộ dataset thành một danh sách, thêm trường `source` và `id`."""

    records: List[Dict[str, object]] = []
    for path in paths if paths is not None else dataset_paths():
        for record in load_dataset(path):
            merged = dict(record)
            merged["source"] = path.name
            merged["id"] = record_id(str(record.get("query", "")))
            records.append(merged)
    return records


def normalize_query(query: str) -> str:
    """Chuẩn hoá truy vấn để so trùng lặp: NFKC, gộp khoảng trắng, hạ chữ."""

    text = unicodedata.normalize("NFKC", query)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def record_id(query: str) -> str:
    """ID ổn định suy ra từ nội dung truy vấn (12 ký tự hex đầu của SHA-1)."""

    return hashlib.sha1(normalize_query(query).encode("utf-8")).hexdigest()[:12]


def tokenize(text: str) -> List[str]:
    """Tách token đơn giản: hạ chữ, giữ chữ/số và dạng rút gọn kiểu `don't`."""

    return _TOKEN_RE.findall(unicodedata.normalize("NFKC", text).lower())


def write_text(path: Path, content: str) -> None:
    """Ghi file UTF-8 với xuống dòng LF, tạo thư mục cha nếu cần."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def write_json(path: Path, data: object) -> None:
    """Ghi JSON UTF-8, thụt lề 2 khoảng trắng, giữ nguyên ký tự Unicode."""

    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def group_by(records: Iterable[Dict[str, object]],
             key: str) -> Dict[object, List[Dict[str, object]]]:
    """Nhóm bản ghi theo giá trị của một trường."""

    buckets: Dict[object, List[Dict[str, object]]] = {}
    for record in records:
        buckets.setdefault(record.get(key), []).append(record)
    return buckets


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[object]],
                   aligns: Sequence[str] | None = None) -> str:
    """Sinh bảng Markdown. `aligns` nhận các giá trị `left`, `right`, `center`."""

    separators = []
    for index in range(len(headers)):
        align = aligns[index] if aligns and index < len(aligns) else "left"
        separators.append({"left": "---", "right": "---:", "center": ":---:"}[align])

    lines = [
        "| " + " | ".join(str(header) for header in headers) + " |",
        "| " + " | ".join(separators) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)
