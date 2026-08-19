# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
đánh phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

Với kho dữ liệu này, quy ước phiên bản được hiểu như sau:

- **MAJOR** — thay đổi schema hoặc ý nghĩa nhãn, phá vỡ tương thích ngược.
- **MINOR** — thêm miền, thêm truy vấn, thêm công cụ.
- **PATCH** — sửa nhãn sai, hiệu đính corpus, sửa lỗi tài liệu.

## [Chưa phát hành]

### Đã thêm

- `tools/` — bộ công cụ chỉ dùng thư viện chuẩn Python:
  - `validate_datasets.py` kiểm định schema, nhãn, miền, trùng lặp trong và giữa các file.
  - `dataset_stats.py` sinh `docs/dataset_stats.md` (có chế độ `--check` cho CI).
  - `make_splits.py` sinh split train/dev/test phân tầng, tái lập được (seed `20260819`).
  - `baseline_router.py` baseline định tuyến TF-IDF + hồi quy logistic, kèm baseline luật,
    kiểm định chéo và đánh giá leave-one-domain-out.
  - `export_dataset.py` xuất bản gộp CSV/JSONL.
  - `dra_utils.py` tiện ích dùng chung (tách token, chuẩn hoá, `id` bản ghi ổn định).
- `tests/test_datasets.py` — 23 test toàn vẹn dữ liệu, tính tái lập và baseline.
- `.github/workflows/ci.yml` — CI trên Python 3.9/3.11/3.12.
- `Makefile` và `tasks.ps1` — trình chạy tác vụ cho Linux/macOS và Windows.
- `datasets/splits/` và `datasets/exports/` — file dẫn xuất sinh từ dữ liệu nguồn.
- `docs/dataset_card.md`, `docs/labeling_guidelines.md`, `docs/dataset_stats.md`,
  `docs/baseline_results.md`.
- `CONTRIBUTING.md`, `CITATION.cff`, `CHANGELOG.md`, `CLAUDE.md`.

### Đã ghi nhận

- Corpus trong `corpus/` trích từ sách giáo khoa OpenStax theo giấy phép
  **CC BY 4.0**, khác với giấy phép MIT của mã nguồn trong kho. Chi tiết trong
  [docs/dataset_card.md](docs/dataset_card.md).

## [1.0.0] - 2026-06-26

### Đã thêm

- Ba bộ dữ liệu truy vấn đã gán nhãn, 336 bản ghi mỗi miền, cân bằng 50/50:
  World History, Microeconomics, Introductory Statistics.
- Ba corpus tham chiếu tương ứng trong `corpus/`.
- Bản thảo bài báo (PDF và DOCX) trong `paper/`.
- `docs/dataset_description.md` và `docs/research_log.md`.
