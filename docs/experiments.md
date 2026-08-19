# Giao thức thí nghiệm

Tài liệu này mô tả các thí nghiệm đã chạy, cách chạy lại, và cách đọc kết quả.
Số liệu cụ thể nằm trong [baseline_results.md](baseline_results.md) và
[../results/baseline_metrics.json](../results/baseline_metrics.json); tài liệu
này giải thích *tại sao* chúng được đo như vậy.

## Câu hỏi nghiên cứu

**RQ1.** Độ phức tạp định tuyến của truy vấn có dự đoán được bằng một bộ phân
loại rẻ, không cần gọi mô hình ngôn ngữ, hay không?

**RQ2.** Bộ phân loại đó học tín hiệu gì — cấu trúc câu hỏi khái quát được, hay
từ vựng riêng của từng miền?

**RQ3.** Một luật viết tay đơn giản (độ dài, từ khoá) đã đủ chưa, hay việc học
thực sự đem lại thêm giá trị?

## Thiết kế

Ba chế độ đánh giá, mỗi chế độ trả lời một câu hỏi khác nhau.

### E1 — Hold-out (RQ1, RQ3)

Huấn luyện trên `datasets/splits/train.json` (708 truy vấn), đánh giá một lần
trên `datasets/splits/test.json` (150 truy vấn). Tập `dev.json` (150) dành cho
việc chỉnh siêu tham số; **tập test chỉ được chạm khi báo cáo kết quả cuối**.

Split phân tầng theo `(domain, label)` với seed `20260819`, nên cả ba tập giữ
nguyên tỉ lệ miền và tỉ lệ nhãn.

Chạy cùng lúc bốn mô hình trên đúng một tập test: `majority`, `keyword`,
`length>=k`, và `tfidf+logreg`. Ba mô hình đầu là mức sàn để đo phần giá trị mà
việc học thực sự đóng góp.

```bash
python tools/baseline_router.py --mode holdout                 # trên tập test
python tools/baseline_router.py --mode holdout --eval-split dev  # khi đang chỉnh
```

### E2 — Kiểm định chéo 5-fold phân tầng (RQ1)

Toàn bộ 1.008 truy vấn được chia thành 5 fold phân tầng theo `(domain, label)`.
Mỗi fold lần lượt làm tập kiểm tra, bốn fold còn lại làm tập huấn luyện.

Mục đích: ước lượng độ chính xác ổn định hơn một lần hold-out duy nhất, và cho
ra độ lệch chuẩn giữa các fold. Độ lệch chuẩn lớn là dấu hiệu tập test 150 truy
vấn quá nhỏ để kết luận chắc chắn.

```bash
python tools/baseline_router.py --mode cv --folds 5
```

### E3 — Leave-one-domain-out (RQ2)

Ba lần chạy. Mỗi lần, hai miền làm tập huấn luyện và miền còn lại làm tập kiểm
tra — miền đó mô hình **chưa từng thấy một truy vấn nào**.

Đây là thí nghiệm quan trọng nhất của kho. Nếu accuracy sụp đổ khi đổi miền,
nghĩa là router chỉ học từ vựng chuyên ngành (`elasticity`, `Versailles`,
`z-score`) và sẽ hỏng ngay khi hệ thống gia sư mở thêm môn mới. Nếu accuracy giữ
được, router đang học cấu trúc câu hỏi — thứ khái quát hoá được.

```bash
python tools/baseline_router.py --mode lodo
```

## Kết quả tóm tắt

| Thí nghiệm | Chỉ số chính | Kết quả |
| --- | --- | --- |
| E1 hold-out | Accuracy (test) | 0,973 |
| E1 mức sàn tốt nhất | Accuracy, `length>=19` | 0,907 |
| E2 kiểm định chéo | Accuracy trung bình | 0,983 ± 0,011 |
| E3 leave-one-domain-out | Accuracy theo miền | 0,955 – 0,988 |

Bảng đầy đủ (precision, recall, F1, ma trận nhầm lẫn) trong
[baseline_results.md](baseline_results.md).

## Cách đọc kết quả

**RQ1 — có.** 0,973 trên tập giữ riêng, với mô hình chạy dưới một mili-giây và
không gọi mạng. Với DRA, đây là bằng chứng tầng định tuyến không cần một lần gọi
LLM riêng.

**RQ2 — cấu trúc câu hỏi.** Khoảng cách giữa E2 (0,983) và E3 (0,955–0,988) rất
nhỏ. Mô hình huấn luyện trên Lịch sử và Kinh tế vẫn định tuyến đúng 95,5% truy
vấn Thống kê dù chưa từng thấy từ vựng thống kê nào. Bảng trọng số trong
[baseline_results.md](baseline_results.md) khẳng định điều này: các đặc trưng
mạnh nhất là `compare`, `how does`, `what is`, `how many` và nhóm độ dài — toàn
là dấu hiệu cấu trúc, không phải thuật ngữ chuyên ngành.

**RQ3 — có, nhưng phần thắng nhỏ hơn vẻ ngoài.** Luật độ dài đơn thuần
(`length >= 19`) đã đạt 0,907. Mô hình học thêm được 6,6 điểm phần trăm. Đối
chiếu từng truy vấn trên tập test: mô hình sửa đúng 12 trường hợp luật độ dài
sai, và làm sai 2 trường hợp luật độ dài đúng. 12 trường hợp được sửa chia đều
hai kiểu, đúng như dự đoán:

- **6 truy vấn factual nhưng dài** (19–23 token), thường là câu hỏi số liệu
  nhiều mệnh đề: *"What was the unemployment rate in the United States in 1939,
  and how low did it drop by 1943?"*
- **6 truy vấn analytical nhưng ngắn** (13–18 token), thường mở đầu bằng
  `Compare` hoặc `How does ... differ`: *"Compare the interpretation of a
  positive z-score versus a negative z-score."*

Nói cách khác, phần giá trị mà việc học đóng góp chính là chỗ độ dài và mức độ
suy luận tách rời nhau.

## Cảnh báo khi diễn giải

- **Con số này là mốc sàn, không phải bài kiểm tra khó.** Truy vấn do nhóm soạn
  nên khuôn mẫu bề mặt khá đều. Xem mục giới hạn trong
  [dataset_card.md](dataset_card.md).
- **Tập test chỉ có 150 truy vấn.** Chênh lệch dưới khoảng 3 điểm phần trăm
  không nên được coi là có ý nghĩa; dùng E2 khi cần so sánh cẩn thận.
- **Chưa có kiểm định ý nghĩa thống kê.** Nếu bài báo cần khẳng định mô hình học
  vượt trội luật độ dài, nên bổ sung kiểm định McNemar trên cùng tập test — xem
  [../ROADMAP.md](../ROADMAP.md).
- **Không có tập kiểm tra đối kháng.** Bộ dữ liệu hiện chưa chứa trường hợp cố
  tình phá heuristic độ dài.

## Chạy lại toàn bộ

```bash
python tools/baseline_router.py --report   # ~17 giây, sinh cả hai file kết quả
python tools/make_figures.py               # sinh figures/*.svg từ kết quả trên
```

Điều kiện tái lập chính xác và cách kiểm chứng nằm trong
[reproducibility.md](reproducibility.md).
