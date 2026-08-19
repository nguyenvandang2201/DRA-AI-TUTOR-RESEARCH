# Lộ trình phát triển

Các hạng mục dưới đây xuất phát từ những giới hạn đã ghi nhận trong
[docs/dataset_card.md](docs/dataset_card.md) và
[docs/experiments.md](docs/experiments.md), sắp theo mức độ ảnh hưởng tới độ tin
cậy của kết quả nghiên cứu.

Lộ trình này là ý định, không phải cam kết thời hạn.

## v1.2 — Làm cho bài kiểm tra khó hơn

Vấn đề cần giải: baseline đạt 0,973 phần lớn vì truy vấn có khuôn mẫu bề mặt rất
đều. Chừng nào chưa khắc phục, mọi cải tiến mô hình đều khó chứng minh.

- [ ] **Tập kiểm tra đối kháng.** Soạn khoảng 100 truy vấn cố tình phá heuristic:
      nhãn `0` nhưng dài và nhiều mệnh đề, nhãn `1` nhưng ngắn gọn. Đặt trong
      `datasets/dataset_adversarial.json` và báo cáo riêng, không trộn vào ba
      miền hiện có.
- [ ] **Kiểm định McNemar** giữa mô hình học và luật độ dài trên cùng tập test,
      để khẳng định phần chênh 6,6 điểm phần trăm là có ý nghĩa thống kê.
- [ ] **Đo độ đồng thuận giữa người gán nhãn.** Người thứ hai gán lại độc lập
      ít nhất 150 truy vấn, báo cáo Cohen's kappa theo quy trình trong
      [docs/labeling_guidelines.md](docs/labeling_guidelines.md).
- [ ] **Rà soát diễn giải lại.** Công cụ hiện chỉ bắt trùng lặp chính xác. Bổ
      sung kiểm tra tương đồng gần (Jaccard trên tập token) để phát hiện hai
      truy vấn chỉ khác cách diễn đạt.

## v1.3 — Mở rộng độ phủ

- [ ] **Thêm miền STEM nâng cao** (ví dụ Calculus hoặc Biology) để kiểm tra xem
      leave-one-domain-out có giữ được kết quả khi từ vựng xa hơn nhiều.
- [ ] **Truy vấn tiếng Việt.** Hệ thống gia sư hướng tới người học Việt Nam
      nhưng toàn bộ truy vấn hiện là tiếng Anh. Cần ít nhất một miền song ngữ để
      biết bộ định tuyến có phụ thuộc ngôn ngữ hay không.
- [ ] **Truy vấn nhiều lượt.** Trong hội thoại thật, "còn cái kia thì sao?" phụ
      thuộc lượt trước. Nhãn hiện tại giả định mỗi truy vấn độc lập.

## v2.0 — Định tuyến nhiều nhánh (phá vỡ tương thích)

DRA thực tế có thể cần hơn hai nhánh. Nhãn hiện tại không phân biệt "cần truy
hồi từ corpus" với "cần tính toán nhiều bước", dù hai nhánh này có chi phí và
thành phần rất khác nhau.

Thay đổi này chạm vào `VALID_LABELS`, `LABEL_NAMES`, khoá phân tầng khi chia
split, và mọi công thức đo nhị phân trong `metrics()`. Vì vậy nó là bản MAJOR.

- [ ] Đề xuất phân loại nhãn 3-4 nhánh, kiểm chứng bằng độ đồng thuận trước khi
      gán lại toàn bộ dữ liệu.
- [ ] Chuyển `metrics()` sang đa lớp (macro/micro, ma trận nhầm lẫn đầy đủ).
- [ ] Giữ ánh xạ về nhãn nhị phân để kết quả cũ vẫn so sánh được.

## Chưa lên lịch

- **Mô hình chi phí thật.** Muốn tuyên bố DRA tiết kiệm bao nhiêu thì cần chi
  phí và độ trễ đo được của từng nhánh, cộng với phân bố truy vấn thật. Kho hiện
  chỉ đo chất lượng quyết định định tuyến.
- **Truy vấn từ log thật.** Có giá trị cao nhưng vướng vấn đề riêng tư; cần quy
  trình ẩn danh và sự đồng ý trước khi thu thập.
- **So sánh với bộ phân loại dùng embedding.** Hữu ích làm cận trên, nhưng sẽ
  phá nguyên tắc không dependency — nếu làm, hãy để ở nhánh riêng và giữ baseline
  thư viện chuẩn làm mốc đối chiếu.
- **Hiệu chuẩn xác suất.** Router thực tế có thể cần ngưỡng khác 0,5 để đánh đổi
  chi phí và chất lượng; cần đường cong hiệu chuẩn và phân tích ngưỡng.

## Việc chăm sóc kho

- [ ] Thêm DOI qua Zenodo sau bản phát hành ổn định đầu tiên
      (xem [docs/reproducibility.md](docs/reproducibility.md)).
- [ ] Bổ sung thông tin ấn bản OpenStax chính xác (tên sách, năm, URL) cho từng
      file corpus.
- [ ] Bật báo cáo coverage lên dịch vụ ngoài nếu muốn có huy hiệu coverage.
