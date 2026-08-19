# Dataset card: DRA AI Tutor routing queries

Thẻ dữ liệu tóm tắt nguồn gốc, mục đích sử dụng và giới hạn của bộ dữ liệu, theo
tinh thần *Datasheets for Datasets* (Gebru et al., 2021).

## 1. Tóm tắt

| Mục | Giá trị |
| --- | --- |
| Tên | DRA AI Tutor routing queries |
| Phiên bản | 1.0.0 |
| Số bản ghi | 1.008 (336 mỗi miền) |
| Miền | World History, Microeconomics, Introductory Statistics |
| Ngôn ngữ truy vấn | Tiếng Anh |
| Nhãn | `0` = factual, `1` = analytical (cân bằng 50/50) |
| Nhiệm vụ | Phân loại nhị phân độ phức tạp truy vấn để định tuyến |
| Định dạng | JSON (nguồn), CSV + JSONL (xuất), split JSON |

Số liệu chi tiết luôn được cập nhật tự động trong [dataset_stats.md](dataset_stats.md).

## 2. Động cơ

Bộ dữ liệu phục vụ đánh giá tầng định tuyến của Dynamic Routing Architecture
(DRA) cho hệ thống AI gia sư: quyết định một truy vấn của người học nên đi vào
nhánh tra cứu rẻ hay nhánh suy luận sâu tốn kém. Câu hỏi nghiên cứu là liệu
quyết định này có thể ra bằng một bộ phân loại rẻ, tất định, thay vì gọi thêm
một mô hình ngôn ngữ lớn.

## 3. Thành phần

Mỗi bản ghi trong `datasets/dataset_<domain>.json`:

```json
{
  "query": "How does the zero-profit point compare to the shutdown point?",
  "domain": "Microeconomics",
  "label": 1
}
```

Các file dẫn xuất **không** phải nguồn sự thật, chúng được sinh lại từ ba file
trên:

- `datasets/splits/{train,dev,test}.json` + `manifest.json` — split phân tầng
  70/15/15 theo `(domain, label)`, seed `20260819`.
- `datasets/exports/dra_queries_all.{csv,jsonl}` — bản gộp, có thêm `id`,
  `label_name`, `n_tokens`, `source`.

Trường `id` là 12 ký tự hex đầu của SHA-1 trên truy vấn đã chuẩn hoá, nên ổn
định giữa các lần sinh và giữa các máy.

## 4. Quy trình thu thập

Truy vấn được soạn từ ba corpus sách giáo khoa mở trong `corpus/`, mỗi truy vấn
trả lời được bằng nội dung corpus tương ứng. Nhãn được gán theo
[labeling_guidelines.md](labeling_guidelines.md). Nhật ký hiệu đính và rà soát
nằm trong [research_log.md](research_log.md).

## 5. Nguồn gốc corpus và giấy phép

`corpus/*.txt` là văn bản trích từ sách giáo khoa **OpenStax**, phát hành theo
**Creative Commons Attribution (CC BY 4.0)**.

Điều này có hệ quả thực tế: mã nguồn và tài liệu trong kho theo giấy phép MIT
(xem `LICENSE`), nhưng **nội dung corpus vẫn thuộc CC BY 4.0** và yêu cầu ghi
công OpenStax khi phát tán lại. Truy vấn trong `datasets/` là văn bản do nhóm
soạn dựa trên corpus, nên cũng nên được ghi công kèm nguồn corpus.

Trước khi phát hành công khai, nên bổ sung thông tin ấn bản chính xác (tên sách,
năm, URL OpenStax) cho từng file corpus.

## 6. Mục đích sử dụng

**Phù hợp:** đánh giá bộ phân loại độ phức tạp truy vấn; so sánh chi phí/độ chính
xác giữa các chiến lược định tuyến; nghiên cứu khái quát hoá liên miền
(leave-one-domain-out).

**Không phù hợp:** đánh giá chất lượng câu trả lời của gia sư; suy ra mức độ
thành thạo của người học; huấn luyện mô hình sinh nội dung giáo dục.

## 7. Giới hạn đã biết

- **Quy mô nhỏ và cân bằng nhân tạo.** Tỉ lệ 50/50 không phản ánh phân bố truy
  vấn thật của người học, vốn thường lệch mạnh về phía factual. Kết quả accuracy
  không chuyển thẳng sang môi trường vận hành.
- **Truy vấn do nhóm soạn, không phải log thật.** Chúng sạch hơn, đúng ngữ pháp
  hơn và ít mơ hồ hơn truy vấn thật.
- **Ba miền, một ngôn ngữ.** Chưa có bằng chứng về STEM nâng cao, ngôn ngữ khác,
  hay truy vấn nhiều lượt hội thoại.
- **Nhãn nhị phân.** DRA thực tế có thể cần nhiều hơn hai nhánh; nhãn hiện tại
  không phân biệt "cần truy hồi" với "cần tính toán".
- **Baseline đạt độ chính xác rất cao** (xem [baseline_results.md](baseline_results.md)).
  Đây vừa là kết quả tích cực vừa là cảnh báo: một phần tín hiệu nằm ở khuôn mẫu
  bề mặt (độ dài, từ mở đầu) do cách soạn truy vấn, nên bộ dữ liệu này nên được
  xem là **mốc sàn**, không phải bài kiểm tra khó.

## 8. Bảo trì

Mọi thay đổi dữ liệu phải qua `python tools/validate_datasets.py --strict` và
sinh lại các file dẫn xuất; xem [../CONTRIBUTING.md](../CONTRIBUTING.md).

## 9. Trích dẫn

Xem `CITATION.cff` ở thư mục gốc.
