"""Sinh hình vẽ SVG cho bài báo, chỉ dùng thư viện chuẩn.

SVG được chọn thay vì PNG vì là vector (không vỡ khi phóng to trong bản in),
là văn bản thuần (git diff được) và không cần matplotlib.

Sinh ra trong `figures/`:

* `fig1_query_length.svg`      -- phân bố độ dài truy vấn theo nhãn.
* `fig2_baseline_accuracy.svg` -- so sánh các mô hình trên tập test.
* `fig3_cross_domain.svg`      -- kết quả leave-one-domain-out.

Chạy: `python tools/make_figures.py`
      `python tools/make_figures.py --check`
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dra_utils import (  # noqa: E402
    REPO_ROOT,
    load_all,
    setup_stdout,
    tokenize,
    write_text,
)

FIGURES_DIR = REPO_ROOT / "figures"
METRICS_PATH = REPO_ROOT / "results" / "baseline_metrics.json"

WIDTH, HEIGHT = 720, 420
MARGIN = {"top": 56, "right": 24, "bottom": 64, "left": 64}

#: Bảng màu an toàn với người mù màu (Okabe-Ito), in đen trắng vẫn phân biệt được.
COLOR_LABEL0 = "#0072B2"
COLOR_LABEL1 = "#D55E00"
COLOR_ACCENT = "#009E73"
COLOR_MUTED = "#999999"
COLOR_TEXT = "#1a1a1a"
COLOR_GRID = "#d8d8d8"

FONT = "font-family=\"Helvetica, Arial, sans-serif\""


def escape(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def svg_header(title: str, subtitle: str) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="{escape(title)}">',
        f"  <title>{escape(title)}</title>",
        f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        f'  <text x="{MARGIN["left"]}" y="28" {FONT} font-size="17" font-weight="600" '
        f'fill="{COLOR_TEXT}">{escape(title)}</text>',
        f'  <text x="{MARGIN["left"]}" y="46" {FONT} font-size="12" '
        f'fill="{COLOR_MUTED}">{escape(subtitle)}</text>',
    ]


def plot_area() -> Tuple[float, float, float, float]:
    """Trả về `(x0, y0, x1, y1)` của vùng vẽ, đã trừ lề."""

    return (MARGIN["left"], MARGIN["top"],
            WIDTH - MARGIN["right"], HEIGHT - MARGIN["bottom"])


def y_axis(y_max: float, ticks: int = 5, percent: bool = False) -> List[str]:
    x0, y0, x1, y1 = plot_area()
    parts = []
    for index in range(ticks + 1):
        value = y_max * index / ticks
        y = y1 - (y1 - y0) * index / ticks
        label = f"{value:.0%}" if percent else f"{value:.0f}"
        parts.append(f'  <line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" '
                     f'stroke="{COLOR_GRID}" stroke-width="1"/>')
        parts.append(f'  <text x="{x0 - 10}" y="{y + 4:.1f}" {FONT} font-size="11" '
                     f'text-anchor="end" fill="{COLOR_MUTED}">{label}</text>')
    return parts


def legend(entries: Sequence[Tuple[str, str]]) -> List[str]:
    """`entries` là danh sách `(nhãn, màu)`, vẽ ở góc trên bên phải."""

    parts = []
    x = WIDTH - MARGIN["right"]
    for label, color in reversed(entries):
        width = 8 + 6.2 * len(label)
        x -= width + 14
        parts.append(f'  <rect x="{x:.1f}" y="34" width="10" height="10" fill="{color}" rx="2"/>')
        parts.append(f'  <text x="{x + 15:.1f}" y="43" {FONT} font-size="11" '
                     f'fill="{COLOR_TEXT}">{escape(label)}</text>')
    return parts


# --------------------------------------------------------------------------
# Hình 1: phân bố độ dài truy vấn
# --------------------------------------------------------------------------

def figure_query_length(bin_size: int = 5, max_tokens: int = 60) -> str:
    records = load_all()
    histograms: Dict[int, Counter] = {0: Counter(), 1: Counter()}
    for record in records:
        n_tokens = min(len(tokenize(str(record["query"]))), max_tokens)
        histograms[int(record["label"])][n_tokens // bin_size] += 1

    n_bins = max_tokens // bin_size + 1
    y_max = max(max(histogram.values()) for histogram in histograms.values())
    y_max = (y_max // 20 + 1) * 20

    x0, y0, x1, y1 = plot_area()
    slot = (x1 - x0) / n_bins
    bar = slot * 0.38

    parts = svg_header(
        "Phân bố độ dài truy vấn theo nhãn",
        f"{len(records)} truy vấn, ba miền gộp lại; độ dài tính bằng token",
    )
    parts += y_axis(y_max)
    parts += legend([("0 · factual", COLOR_LABEL0), ("1 · analytical", COLOR_LABEL1)])

    for bin_index in range(n_bins):
        for offset, (label, color) in enumerate(((0, COLOR_LABEL0), (1, COLOR_LABEL1))):
            count = histograms[label][bin_index]
            if not count:
                continue
            height = (y1 - y0) * count / y_max
            x = x0 + slot * bin_index + slot / 2 + (offset - 1) * bar
            parts.append(f'  <rect x="{x:.1f}" y="{y1 - height:.1f}" width="{bar:.1f}" '
                         f'height="{height:.1f}" fill="{color}" rx="1"/>')

        if bin_index % 2 == 0:
            tick = bin_index * bin_size
            label = f"{tick}+" if tick >= max_tokens else str(tick)
            parts.append(f'  <text x="{x0 + slot * bin_index + slot / 2:.1f}" y="{y1 + 18}" '
                         f'{FONT} font-size="11" text-anchor="middle" '
                         f'fill="{COLOR_MUTED}">{label}</text>')

    parts.append(f'  <line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" '
                 f'stroke="{COLOR_TEXT}" stroke-width="1.5"/>')
    parts.append(f'  <text x="{(x0 + x1) / 2:.1f}" y="{HEIGHT - 20}" {FONT} font-size="12" '
                 f'text-anchor="middle" fill="{COLOR_TEXT}">Số token trong truy vấn</text>')
    parts.append(f'  <text x="18" y="{(y0 + y1) / 2:.1f}" {FONT} font-size="12" '
                 f'text-anchor="middle" fill="{COLOR_TEXT}" '
                 f'transform="rotate(-90 18 {(y0 + y1) / 2:.1f})">Số truy vấn</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------
# Hình 2 và 3: biểu đồ cột từ kết quả baseline
# --------------------------------------------------------------------------

def bar_chart(title: str, subtitle: str, series: Sequence[Tuple[str, float, str]],
              axis_label: str, baseline: float | None = None) -> str:
    """Biểu đồ cột ngang đơn giản; `series` là `(nhãn, giá trị 0-1, màu)`."""

    x0, y0, x1, y1 = plot_area()
    parts = svg_header(title, subtitle)

    label_width = 150
    track_x0 = x0 + label_width
    # Chua cho ra 46px ben phai de nhan gia tri khong bi cat mep hinh.
    track_x1 = x1 - 46
    slot = (y1 - y0) / len(series)
    bar_height = min(slot * 0.55, 34)

    for index in range(6):
        value = index / 5
        x = track_x0 + (track_x1 - track_x0) * value
        parts.append(f'  <line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" '
                     f'stroke="{COLOR_GRID}" stroke-width="1"/>')
        parts.append(f'  <text x="{x:.1f}" y="{y1 + 18}" {FONT} font-size="11" '
                     f'text-anchor="middle" fill="{COLOR_MUTED}">{value:.0%}</text>')

    for index, (label, value, color) in enumerate(series):
        center = y0 + slot * (index + 0.5)
        width = (track_x1 - track_x0) * max(value, 0.0)
        parts.append(f'  <text x="{track_x0 - 12}" y="{center + 4:.1f}" {FONT} font-size="12" '
                     f'text-anchor="end" fill="{COLOR_TEXT}">{escape(label)}</text>')
        parts.append(f'  <rect x="{track_x0}" y="{center - bar_height / 2:.1f}" '
                     f'width="{width:.1f}" height="{bar_height:.1f}" fill="{color}" rx="2"/>')
        parts.append(f'  <text x="{track_x0 + width + 8:.1f}" y="{center + 4:.1f}" {FONT} '
                     f'font-size="12" font-weight="600" fill="{COLOR_TEXT}">'
                     f'{value:.3f}</text>')

    if baseline is not None:
        x = track_x0 + (track_x1 - track_x0) * baseline
        parts.append(f'  <line x1="{x:.1f}" y1="{y0 - 6}" x2="{x:.1f}" y2="{y1 + 4}" '
                     f'stroke="{COLOR_MUTED}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        parts.append(f'  <text x="{x + 6:.1f}" y="{y0 - 10}" {FONT} font-size="11" '
                     f'fill="{COLOR_MUTED}">mức đoán bừa</text>')

    parts.append(f'  <text x="{(track_x0 + track_x1) / 2:.1f}" y="{HEIGHT - 20}" {FONT} '
                 f'font-size="12" text-anchor="middle" fill="{COLOR_TEXT}">'
                 f'{escape(axis_label)}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def load_metrics() -> Dict[str, object]:
    if not METRICS_PATH.exists():
        raise SystemExit(f"Thiếu {METRICS_PATH}. Chạy trước: "
                         f"python tools/baseline_router.py --report")
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


DISPLAY_NAMES = {
    "tfidf+logreg": "TF-IDF + logistic",
    "keyword": "Luật từ khoá",
    "majority": "Đoán nhãn đa số",
}


def figure_baseline_accuracy() -> str:
    holdout = load_metrics()["holdout"]
    ordered = sorted(holdout.items(), key=lambda item: item[1]["accuracy"], reverse=True)

    series = []
    for name, values in ordered:
        display = DISPLAY_NAMES.get(name, name.replace("length>=", "Ngưỡng độ dài ≥ "))
        color = COLOR_ACCENT if name == "tfidf+logreg" else COLOR_LABEL0
        if name == "majority":
            color = COLOR_MUTED
        series.append((display, values["accuracy"], color))

    return bar_chart(
        "So sánh baseline định tuyến trên tập test",
        "150 truy vấn giữ riêng, cân bằng nhãn 75/75",
        series,
        "Accuracy",
        baseline=0.5,
    )


def figure_cross_domain() -> str:
    lodo = load_metrics()["leave_one_domain_out"]
    ordered = sorted(lodo.items(), key=lambda item: item[1]["accuracy"], reverse=True)
    series = [(name, values["accuracy"], COLOR_ACCENT) for name, values in ordered]

    return bar_chart(
        "Khái quát hoá liên miền (leave-one-domain-out)",
        "Huấn luyện trên hai miền, đánh giá trên miền chưa từng thấy",
        series,
        "Accuracy trên miền giữ riêng",
        baseline=0.5,
    )


def build_all() -> Dict[Path, str]:
    return {
        FIGURES_DIR / "fig1_query_length.svg": figure_query_length(),
        FIGURES_DIR / "fig2_baseline_accuracy.svg": figure_baseline_accuracy(),
        FIGURES_DIR / "fig3_cross_domain.svg": figure_cross_domain(),
    }


def main() -> int:
    setup_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="thoát với mã 1 nếu hình vẽ đã lỗi thời")
    args = parser.parse_args()

    figures = build_all()

    if args.check:
        stale = [path for path, content in figures.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            names = ", ".join(path.name for path in stale)
            print(f"Hình vẽ đã lỗi thời ({names}). Chạy: python tools/make_figures.py",
                  file=sys.stderr)
            return 1
        print("Hình vẽ đã cập nhật.")
        return 0

    for path, content in figures.items():
        write_text(path, content)
        print(f"Đã ghi {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
