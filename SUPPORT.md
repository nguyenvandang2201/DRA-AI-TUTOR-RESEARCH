# Nhận hỗ trợ

Dự án nghiên cứu do một người duy trì. Không có cam kết thời gian phản hồi,
nhưng mọi câu hỏi hợp lý đều được đọc.

## Trước khi hỏi

Phần lớn câu hỏi đã có sẵn câu trả lời:

| Bạn muốn biết | Đọc ở đây |
| --- | --- |
| Nhãn `0`/`1` nghĩa là gì, gán nhãn thế nào | [docs/labeling_guidelines.md](docs/labeling_guidelines.md) |
| Dữ liệu từ đâu, dùng được vào việc gì, giới hạn nào | [docs/dataset_card.md](docs/dataset_card.md) |
| Vì sao không dùng scikit-learn, vì sao accuracy cao | [docs/faq.md](docs/faq.md) |
| Cách chạy lại toàn bộ kết quả | [docs/reproducibility.md](docs/reproducibility.md) |
| Thí nghiệm được thiết kế ra sao | [docs/experiments.md](docs/experiments.md) |
| Chi tiết toán học của baseline | [docs/algorithm.md](docs/algorithm.md) |
| Cách đóng góp dữ liệu hoặc mã | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Kế hoạch sắp tới | [ROADMAP.md](ROADMAP.md) |

## Kênh liên hệ

| Việc cần làm | Kênh |
| --- | --- |
| Báo lỗi mã nguồn hoặc công cụ | [Issue: Bug report](../../issues/new?template=bug_report.yml) |
| Báo truy vấn sai nhãn hoặc lỗi dữ liệu | [Issue: Vấn đề dữ liệu](../../issues/new?template=data_issue.yml) |
| Đề xuất tính năng hoặc miền mới | [Issue: Feature request](../../issues/new?template=feature_request.yml) |
| Câu hỏi về nghiên cứu, hợp tác học thuật | Email `ngvandang9999@gmail.com` |
| Vấn đề bảo mật hoặc dữ liệu cá nhân | [SECURITY.md](SECURITY.md) — **không** mở issue công khai |

## Khi báo lỗi, xin kèm

- Phiên bản Python (`python --version`) và hệ điều hành.
- Commit đang dùng (`git rev-parse --short HEAD`).
- Lệnh đã chạy và toàn bộ thông báo lỗi.

Với lỗi liên quan tới kết quả không khớp, xin chạy trước và đính kèm kết quả:

```bash
python tools/validate_datasets.py --strict
git status
```
