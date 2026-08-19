# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
đánh phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

Với kho dữ liệu này, quy ước phiên bản được hiểu như sau:

- **MAJOR** — thay đổi schema hoặc ý nghĩa nhãn, phá vỡ tương thích ngược.
- **MINOR** — thêm miền, thêm truy vấn, thêm công cụ.
- **PATCH** — sửa nhãn sai, hiệu đính corpus, sửa lỗi tài liệu.

## [Chưa phát hành]

Chưa có thay đổi nào.

## [1.1.0] - 2026-08-19

Bản này bổ sung toàn bộ hạ tầng nghiên cứu quanh dữ liệu đã có: công cụ, kiểm
thử, CI, kết quả baseline và tài liệu. **Dữ liệu nguồn không đổi** — ba file
`datasets/dataset_*.json` giữ nguyên 1.008 bản ghi.

### Đã thêm — công cụ

- `tools/validate_datasets.py` kiểm định schema, nhãn, miền, trùng lặp trong và
  giữa các file.
- `tools/make_splits.py` sinh split train/dev/test phân tầng, tái lập được
  (seed `20260819`).
- `tools/baseline_router.py` baseline định tuyến TF-IDF + hồi quy logistic, kèm
  baseline luật, kiểm định chéo và đánh giá leave-one-domain-out.
- `tools/dataset_stats.py` sinh `docs/dataset_stats.md`.
- `tools/export_dataset.py` xuất bản gộp CSV/JSONL.
- `tools/make_figures.py` sinh hình SVG cho bài báo, không cần matplotlib.
- `tools/dra_utils.py` tiện ích dùng chung (tách token, chuẩn hoá, `id` ổn định).

Mọi script sinh file đều có cờ `--check` để CI phát hiện file dẫn xuất lỗi thời.

### Đã thêm — kết quả

- `docs/baseline_results.md` và `results/baseline_metrics.json`: hold-out 0,973;
  kiểm định chéo 5-fold 0,983 ± 0,011; leave-one-domain-out 0,955–0,988.
- `figures/fig1_query_length.svg`, `fig2_baseline_accuracy.svg`,
  `fig3_cross_domain.svg`.
- `datasets/splits/` (708/150/150) và `datasets/exports/` (CSV + JSONL).
- `docs/dataset_stats.md`.

### Đã thêm — kiểm thử và CI

- `tests/test_datasets.py`: 23 test về toàn vẹn dữ liệu, tính tái lập và baseline.
- `.github/workflows/ci.yml`: bốn job — kiểm định trên Python 3.9/3.11/3.12,
  xác nhận kết quả tái lập được, lint bằng ruff, và đo coverage.
- `.github/workflows/release.yml`: tự tạo GitHub Release khi đẩy tag `vX.Y.Z`,
  kèm gói dữ liệu và ghi chú trích từ file này.
- `.github/ISSUE_TEMPLATE/` (gồm mẫu riêng để báo truy vấn sai nhãn),
  `PULL_REQUEST_TEMPLATE.md`, `dependabot.yml`.

### Đã thêm — tài liệu

- `docs/architecture.md`, `docs/algorithm.md`, `docs/experiments.md`,
  `docs/reproducibility.md`, `docs/faq.md`, `docs/dataset_card.md`,
  `docs/labeling_guidelines.md`.
- `ROADMAP.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
  `SUPPORT.md`, `AUTHORS.md`, `CITATION.cff`, `CHANGELOG.md`, `CLAUDE.md`.

### Đã thêm — cấu hình

- `pyproject.toml` (metadata + cấu hình ruff/coverage; **không có dependency
  runtime**), `requirements-dev.txt`, `.editorconfig`, `.gitattributes`,
  `.python-version`, `Dockerfile`, `.dockerignore`.
- `Makefile` và `tasks.ps1` làm trình chạy tác vụ cho Linux/macOS và Windows.

### Đã ghi nhận

- Corpus trong `corpus/` trích từ sách giáo khoa OpenStax theo giấy phép
  **CC BY 4.0**, khác với giấy phép MIT của mã nguồn trong kho. Chi tiết trong
  [docs/dataset_card.md](docs/dataset_card.md).
- Baseline đạt 0,97–0,98 một phần vì truy vấn do nhóm soạn có khuôn mẫu bề mặt
  khá đều. Bộ dữ liệu nên được xem là mốc sàn, không phải bài kiểm tra khó; xem
  [ROADMAP.md](ROADMAP.md) mục v1.2.

## [1.0.0] - 2026-06-26

### Đã thêm

- Ba bộ dữ liệu truy vấn đã gán nhãn, 336 bản ghi mỗi miền, cân bằng 50/50:
  World History, Microeconomics, Introductory Statistics.
- Ba corpus tham chiếu tương ứng trong `corpus/`.
- Bản thảo bài báo (PDF và DOCX) trong `paper/`.
- `docs/dataset_description.md` và `docs/research_log.md`.

[Chưa phát hành]: https://github.com/nguyenvandang2201/DRA-AI-TUTOR-RESEARCH/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/nguyenvandang2201/DRA-AI-TUTOR-RESEARCH/releases/tag/v1.1.0
[1.0.0]: https://github.com/nguyenvandang2201/DRA-AI-TUTOR-RESEARCH/releases/tag/v1.0.0
