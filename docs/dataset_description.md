# Dataset Description

Tài liệu này mô tả các bộ dữ liệu trong thư mục `datasets/` và corpus tham
chiếu trong `corpus/`.

Xem thêm: [dataset_card.md](dataset_card.md) (nguồn gốc, giới hạn),
[labeling_guidelines.md](labeling_guidelines.md) (định nghĩa nhãn),
[dataset_stats.md](dataset_stats.md) (số liệu chi tiết, sinh tự động).

## File dữ liệu

| File | Domain | Số bản ghi | Phân bố nhãn |
| --- | --- | ---: | --- |
| `dataset_introductory_statistics.json` | Introductory Statistics | 336 | `0`: 168, `1`: 168 |
| `dataset_microeconomics.json` | Microeconomics | 336 | `0`: 168, `1`: 168 |
| `dataset_world_history.json` | World History | 336 | `0`: 168, `1`: 168 |

Ba file trên là **nguồn sự thật duy nhất**. Các thư mục `datasets/splits/` và
`datasets/exports/` được sinh tự động từ chúng, đừng sửa tay.

## Schema

Mỗi file JSON là một mảng object có cùng cấu trúc, đúng ba trường:

```json
{
  "query": "In what year was the Triple Entente formally created between Russia, France, and Britain?",
  "domain": "World History",
  "label": 0
}
```

- `query`: câu hỏi hoặc yêu cầu người học gửi cho hệ thống gia sư (tiếng Anh,
  chuẩn hoá Unicode NFC).
- `domain`: miền kiến thức của truy vấn; phải khớp với tên file theo ánh xạ
  `DOMAIN_BY_SLUG` trong [../tools/dra_utils.py](../tools/dra_utils.py).
- `label`: nhãn độ phức tạp định tuyến. `0` = factual (câu hỏi trực tiếp, tra cứu
  được); `1` = analytical (cần so sánh, tổng hợp hoặc lập luận nhiều bước).
  Quy tắc quyết định đầy đủ nằm trong [labeling_guidelines.md](labeling_guidelines.md).

## File dẫn xuất

| Đường dẫn | Nội dung | Sinh bởi |
| --- | --- | --- |
| `datasets/splits/train.json` | 708 bản ghi (70%) | `tools/make_splits.py` |
| `datasets/splits/dev.json` | 150 bản ghi (15%) | `tools/make_splits.py` |
| `datasets/splits/test.json` | 150 bản ghi (15%) | `tools/make_splits.py` |
| `datasets/splits/manifest.json` | Seed, tỉ lệ, số lượng theo nhãn và miền | `tools/make_splits.py` |
| `datasets/exports/dra_queries_all.csv` | Bản gộp 1.008 dòng cho Excel/pandas/R | `tools/export_dataset.py` |
| `datasets/exports/dra_queries_all.jsonl` | Bản gộp, một bản ghi mỗi dòng | `tools/export_dataset.py` |

Split được phân tầng theo cặp `(domain, label)` với seed `20260819`, nên mọi
split giữ nguyên tỉ lệ miền và tỉ lệ nhãn của dữ liệu gốc và tái lập được trên
mọi máy.

Bản dẫn xuất có thêm trường `id` — 12 ký tự hex đầu của SHA-1 trên truy vấn đã
chuẩn hoá. Đây là khoá ổn định để đối chiếu bản ghi giữa các file mà không phụ
thuộc thứ tự.

## Corpus tham chiếu

| File | Mục đích |
| --- | --- |
| `introductory_statistics.txt` | Nguồn tham chiếu cho truy vấn thống kê nhập môn. |
| `microeconomics.txt` | Nguồn tham chiếu cho truy vấn kinh tế vi mô. |
| `world_history.txt` | Nguồn tham chiếu cho truy vấn lịch sử thế giới. |

Corpus trích từ sách giáo khoa OpenStax theo giấy phép CC BY 4.0; xem
[dataset_card.md](dataset_card.md) mục nguồn gốc và giấy phép.

## Quy trình kiểm tra

Trước khi commit thay đổi dữ liệu:

```bash
python tools/validate_datasets.py --strict
```

Công cụ này kiểm tra JSON hợp lệ, schema đúng ba trường, kiểu và miền giá trị
của `label`, sự khớp giữa `domain` và tên file, ký tự điều khiển hoặc hỏng mã
hoá trong `query`, cân bằng nhãn, và truy vấn trùng lặp cả trong lẫn giữa các
file.

Sau đó sinh lại file dẫn xuất và chạy test:

```bash
python tools/make_splits.py
python tools/dataset_stats.py
python tools/export_dataset.py
python -m unittest discover -s tests -v
```

Hoặc gọn hơn: `./tasks.ps1 all` (Windows) / `make all` (Linux, macOS).
