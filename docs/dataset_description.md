# Dataset Description

Tài liệu này mô tả các bộ dữ liệu trong thư mục `datasets/` và corpus tham
chiếu trong `corpus/`.

## File dữ liệu

| File | Domain | Số bản ghi | Phân bố nhãn |
| --- | --- | ---: | --- |
| `dataset_introductory_statistics.json` | Introductory Statistics | 336 | `0`: 168, `1`: 168 |
| `dataset_microeconomics.json` | Microeconomics | 336 | `0`: 168, `1`: 168 |
| `dataset_world_history.json` | World History | 336 | `0`: 168, `1`: 168 |

## Schema

Mỗi file JSON là một mảng object có cùng cấu trúc:

```json
{
  "query": "In what year was the Triple Entente formally created between Russia, France, and Britain?",
  "domain": "World History",
  "label": 0
}
```

- `query`: câu hỏi hoặc yêu cầu người học gửi cho hệ thống gia sư.
- `domain`: miền kiến thức của truy vấn.
- `label`: nhãn độ phức tạp định tuyến. Theo dữ liệu hiện tại, `0` thường là
  câu hỏi trực tiếp/thực kiện; `1` thường là câu hỏi phân tích, so sánh hoặc cần
  lập luận nhiều bước.

## Corpus tham chiếu

| File | Mục đích |
| --- | --- |
| `introductory_statistics.txt` | Nguồn tham chiếu cho truy vấn thống kê nhập môn. |
| `microeconomics.txt` | Nguồn tham chiếu cho truy vấn kinh tế vi mô. |
| `world_history.txt` | Nguồn tham chiếu cho truy vấn lịch sử thế giới. |

