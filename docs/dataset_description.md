# Dataset Description

Tài liệu này mô tả các bộ dữ liệu trong thư mục `datasets/` và corpus tham
chiếu trong `corpus/`.

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

