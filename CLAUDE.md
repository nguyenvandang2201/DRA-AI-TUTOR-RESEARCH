# CLAUDE.md

Ghi chú cho Claude Code khi làm việc trong kho này.

## Kho này là gì

Kho nghiên cứu (không phải ứng dụng) cho đề tài Dynamic Routing Architecture
(DRA) trong hệ thống AI gia sư. Nhiệm vụ trung tâm: phân loại truy vấn của người
học thành `0` = factual (định tuyến sang nhánh rẻ) hoặc `1` = analytical (định
tuyến sang nhánh suy luận sâu).

## Nguồn sự thật và file dẫn xuất

Chỉ ba file sau được sửa tay:

```
datasets/dataset_introductory_statistics.json
datasets/dataset_microeconomics.json
datasets/dataset_world_history.json
```

Mọi thứ dưới đây được **sinh tự động**, đừng sửa tay:

| File dẫn xuất | Sinh bởi |
| --- | --- |
| `datasets/splits/*.json` | `python tools/make_splits.py` |
| `datasets/exports/*` | `python tools/export_dataset.py` |
| `docs/dataset_stats.md` | `python tools/dataset_stats.py` |
| `docs/baseline_results.md` | `python tools/baseline_router.py --report` |
| `results/baseline_metrics.json` | `python tools/baseline_router.py --report` |
| `figures/*.svg` | `python tools/make_figures.py` |

Sau khi đổi dữ liệu nguồn, phải sinh lại tất cả — CI kiểm tra bằng các cờ
`--check` và sẽ fail nếu lệch.

## Lệnh thường dùng

```powershell
./tasks.ps1 check      # giống hệt CI: validate + check dẫn xuất + test
./tasks.ps1 all        # sinh lại mọi thứ rồi chạy test
python -m unittest discover -s tests -v
python tools/baseline_router.py --predict "How does X compare to Y?"
```

`lint` và `coverage` cần `pip install -r requirements-dev.txt`; chúng là công cụ
phát triển tuỳ chọn, không bao giờ cần để sinh lại kết quả.

Trên Linux/macOS dùng `make check`, `make all`.

## Ràng buộc kỹ thuật

- **Không thêm dependency.** Toàn bộ `tools/` chạy bằng thư viện chuẩn Python
  3.9+. Đây là chủ ý: số liệu trong bài báo phải lặp lại được trên máy trống.
  Nếu cần numpy/scikit-learn cho một thí nghiệm, hãy hỏi trước.
- **Mọi thứ phải tất định.** Sắp xếp trước khi trộn, seed tường minh, phá hoà
  bằng khoá phụ (`PYTHONHASHSEED` không được ảnh hưởng kết quả).
- **UTF-8 mọi nơi.** Corpus Thống kê chứa `μ`, `σ`, `²`. Script nào in ra màn
  hình phải gọi `dra_utils.setup_stdout()`, nếu không sẽ vỡ trên console Windows
  (cp1252). Ghi file luôn qua `write_text` / `write_json` (UTF-8, xuống dòng LF).
- **Chuẩn hoá Unicode:** dữ liệu ở dạng NFC. Đừng chạy NFKC lên `query` — nó biến
  `1 – r²` thành `1 - r2` và làm hỏng ký hiệu thống kê. NFKC chỉ dùng nội bộ khi
  so trùng lặp.

## Quy ước viết

- Chú thích, docstring, thông báo lỗi và tài liệu viết bằng **tiếng Việt**.
- Nội dung dữ liệu (`query`, `domain`) giữ nguyên **tiếng Anh**.
- Commit message dùng tiền tố Conventional Commits, mô tả tiếng Việt.

## Giấy phép cần lưu ý

Mã nguồn và tài liệu theo MIT (`LICENSE`), nhưng `corpus/*.txt` trích từ sách
OpenStax theo **CC BY 4.0**. Khi tạo nội dung phái sinh hoặc hướng dẫn phát tán,
nhớ giữ phần ghi công OpenStax. Chi tiết trong `docs/dataset_card.md`.

## Tài liệu liên quan

- [docs/labeling_guidelines.md](docs/labeling_guidelines.md) — định nghĩa nhãn, trường hợp ranh giới.
- [docs/dataset_card.md](docs/dataset_card.md) — nguồn gốc, giới hạn đã biết.
- [docs/architecture.md](docs/architecture.md) — luồng dữ liệu và ba nguyên tắc kiến trúc.
- [docs/algorithm.md](docs/algorithm.md) — đặc tả toán học của baseline.
- [docs/experiments.md](docs/experiments.md) — thiết kế thí nghiệm và cách đọc kết quả.
- [docs/faq.md](docs/faq.md) — vì sao không dùng scikit-learn, vì sao accuracy cao.
- [CONTRIBUTING.md](CONTRIBUTING.md) — quy trình thay đổi dữ liệu.
