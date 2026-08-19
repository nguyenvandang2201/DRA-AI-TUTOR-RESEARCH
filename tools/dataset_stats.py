"""Sinh báo cáo thống kê mô tả cho `datasets/` và `corpus/`.

Chạy: `python tools/dataset_stats.py`          -> ghi docs/dataset_stats.md
      `python tools/dataset_stats.py --check`  -> chỉ kiểm tra báo cáo đã cập nhật
      `python tools/dataset_stats.py --stdout` -> in ra màn hình, không ghi file
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dra_utils import (  # noqa: E402
    CORPUS_DIR,
    DOCS_DIR,
    LABEL_NAMES,
    dataset_paths,
    group_by,
    load_all,
    markdown_table,
    setup_stdout,
    tokenize,
    write_text,
)

OUTPUT_PATH = DOCS_DIR / "dataset_stats.md"

#: Từ mở đầu câu hỏi được theo dõi riêng vì chúng gợi ý mức độ suy luận.
QUESTION_OPENERS = (
    "what", "who", "when", "where", "which", "how", "why",
    "define", "list", "compare", "explain", "describe", "analyze", "evaluate",
)


def length_stats(records: Sequence[Dict[str, object]]) -> Dict[str, float]:
    words = [len(tokenize(str(record["query"]))) for record in records]
    chars = [len(str(record["query"])) for record in records]
    multi = sum(1 for record in records if str(record["query"]).count("?") > 1)
    return {
        "n": len(records),
        "words_mean": statistics.fmean(words),
        "words_median": statistics.median(words),
        "words_min": min(words),
        "words_max": max(words),
        "chars_mean": statistics.fmean(chars),
        "multi_question_pct": 100.0 * multi / len(records),
    }


def log_odds(records: Sequence[Dict[str, object]], top_n: int = 12,
             min_count: int = 8) -> List[Tuple[str, float, int, int]]:
    """Từ khoá phân biệt nhãn 1 với nhãn 0 theo log-odds có làm mượt Laplace.

    Trả về danh sách `(token, score, count_label1, count_label0)`; điểm dương
    nghiêng về nhãn 1 (analytical), điểm âm nghiêng về nhãn 0 (factual).
    """

    counts = {0: Counter(), 1: Counter()}
    for record in records:
        counts[int(record["label"])].update(set(tokenize(str(record["query"]))))

    totals = {label: sum(counter.values()) for label, counter in counts.items()}
    vocab = set(counts[0]) | set(counts[1])

    scored: List[Tuple[str, float, int, int]] = []
    for token in sorted(vocab):
        c1, c0 = counts[1][token], counts[0][token]
        if c1 + c0 < min_count:
            continue
        p1 = (c1 + 1) / (totals[1] + len(vocab))
        p0 = (c0 + 1) / (totals[0] + len(vocab))
        scored.append((token, math.log(p1 / p0), c1, c0))

    # Sắp xếp có phá hoà (token) để báo cáo tái lập được giữa các lần chạy.
    top = sorted(scored, key=lambda item: (-item[1], item[0]))[:top_n]
    bottom = sorted(scored, key=lambda item: (item[1], item[0]))[:top_n]
    return top + bottom


def opener_distribution(records: Sequence[Dict[str, object]]) -> Counter:
    counter: Counter = Counter()
    for record in records:
        tokens = tokenize(str(record["query"]))
        first = tokens[0] if tokens else ""
        counter[first if first in QUESTION_OPENERS else "(khác)"] += 1
    return counter


def corpus_rows() -> List[Sequence[object]]:
    rows: List[Sequence[object]] = []
    for path in sorted(CORPUS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rows.append((
            "`" + path.name + "`",
            f"{len(text.splitlines()):,}",
            f"{len(tokenize(text)):,}",
            f"{len(text) / 1024:.0f} KB",
        ))
    return rows


def build_report() -> str:
    records = load_all()
    by_domain = group_by(records, "domain")

    lines: List[str] = [
        "# Thống kê bộ dữ liệu",
        "",
        "File này được sinh tự động bởi `python tools/dataset_stats.py`.",
        "Đừng sửa tay: hãy chạy lại script sau khi thay đổi dữ liệu.",
        "",
        "## Tổng quan",
        "",
    ]

    overview_rows: List[Sequence[object]] = []
    for path in dataset_paths():
        subset = [record for record in records if record["source"] == path.name]
        labels = Counter(int(record["label"]) for record in subset)
        overview_rows.append((
            "`" + path.name + "`",
            str(subset[0]["domain"]) if subset else "-",
            len(subset),
            labels[0],
            labels[1],
            f"{100 * labels[1] / len(subset):.1f}%" if subset else "-",
        ))
    total_labels = Counter(int(record["label"]) for record in records)
    overview_rows.append((
        "**Tổng**", "-", len(records), total_labels[0], total_labels[1],
        f"{100 * total_labels[1] / len(records):.1f}%",
    ))
    lines.append(markdown_table(
        ["File", "Domain", "Bản ghi", "Nhãn 0", "Nhãn 1", "Tỷ lệ nhãn 1"],
        overview_rows,
        ["left", "left", "right", "right", "right", "right"],
    ))

    lines += ["", "## Độ dài truy vấn theo miền và nhãn", "",
              "Độ dài tính bằng token (tách theo `dra_utils.tokenize`).", ""]
    length_rows: List[Sequence[object]] = []
    for domain in sorted(by_domain):
        for label in (0, 1):
            subset = [record for record in by_domain[domain] if int(record["label"]) == label]
            if not subset:
                continue
            stats = length_stats(subset)
            length_rows.append((
                domain,
                f"{label} ({LABEL_NAMES[label]})",
                stats["n"],
                f"{stats['words_mean']:.1f}",
                f"{stats['words_median']:.0f}",
                f"{stats['words_min']}-{stats['words_max']}",
                f"{stats['chars_mean']:.0f}",
                f"{stats['multi_question_pct']:.1f}%",
            ))
    lines.append(markdown_table(
        ["Domain", "Nhãn", "n", "Token TB", "Trung vị", "Min-Max", "Ký tự TB", "Nhiều dấu hỏi"],
        length_rows,
        ["left", "left", "right", "right", "right", "center", "right", "right"],
    ))
    lines += ["",
              "Khoảng cách độ dài giữa hai nhãn là tín hiệu định tuyến rẻ nhất: truy vấn",
              "analytical dài hơn đáng kể vì thường ghép nhiều mệnh đề so sánh hoặc giải thích.",
              ""]

    lines += ["## Từ mở đầu truy vấn", ""]
    openers_by_label = {
        label: opener_distribution([record for record in records if int(record["label"]) == label])
        for label in (0, 1)
    }
    all_openers = sorted(
        set(openers_by_label[0]) | set(openers_by_label[1]),
        key=lambda token: (-(openers_by_label[0][token] + openers_by_label[1][token]), token),
    )
    lines.append(markdown_table(
        ["Từ mở đầu", "Nhãn 0", "Nhãn 1", "Tổng"],
        [("`" + opener + "`", openers_by_label[0][opener], openers_by_label[1][opener],
          openers_by_label[0][opener] + openers_by_label[1][opener]) for opener in all_openers],
        ["left", "right", "right", "right"],
    ))

    lines += ["", "## Từ khoá phân biệt nhãn", "",
              "Điểm log-odds (làm mượt Laplace) trên tần suất tài liệu; điểm dương nghiêng",
              "về nhãn 1, điểm âm nghiêng về nhãn 0.", ""]
    lines.append(markdown_table(
        ["Token", "Log-odds", "Truy vấn nhãn 1", "Truy vấn nhãn 0"],
        [("`" + token + "`", f"{score:+.2f}", c1, c0)
         for token, score, c1, c0 in log_odds(records)],
        ["left", "right", "right", "right"],
    ))

    lines += ["", "## Corpus tham chiếu", ""]
    lines.append(markdown_table(
        ["File", "Dòng", "Token", "Kích thước"],
        corpus_rows(),
        ["left", "right", "right", "right"],
    ))

    lines += ["", "## Trùng lặp", ""]
    unique_ids = Counter(record["id"] for record in records)
    duplicate_groups = sum(1 for count in unique_ids.values() if count > 1)
    lines += [
        f"- Truy vấn duy nhất: {len(unique_ids):,} / {len(records):,}",
        f"- Nhóm truy vấn trùng lặp (sau chuẩn hoá): {duplicate_groups}",
        "",
    ]

    return "\n".join(lines)


def main() -> int:
    setup_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="thoát với mã 1 nếu docs/dataset_stats.md chưa được cập nhật")
    parser.add_argument("--stdout", action="store_true", help="in báo cáo thay vì ghi file")
    args = parser.parse_args()

    report = build_report()

    if args.stdout:
        print(report)
        return 0

    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != report:
            print(f"{OUTPUT_PATH} đã lỗi thời. Chạy: python tools/dataset_stats.py",
                  file=sys.stderr)
            return 1
        print(f"{OUTPUT_PATH} đã cập nhật.")
        return 0

    write_text(OUTPUT_PATH, report)
    print(f"Đã ghi {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
