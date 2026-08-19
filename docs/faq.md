# Câu hỏi thường gặp

## Về bộ dữ liệu

### Nhãn `0` và `1` nghĩa là gì?

`0` = factual: trả lời được bằng tra cứu trực tiếp, định tuyến sang nhánh rẻ.
`1` = analytical: cần suy luận nhiều bước, định tuyến sang nhánh đắt. Quy tắc
quyết định đầy đủ nằm trong [labeling_guidelines.md](labeling_guidelines.md).

### Tại sao tỉ lệ nhãn đúng 50/50?

Để accuracy có ý nghĩa mà không cần cân nhắc phân bố lệch, và để mọi split đều
cân bằng. Đây **không** phải phân bố truy vấn thật của người học — thực tế
thường lệch mạnh về factual. Xem mục giới hạn trong
[dataset_card.md](dataset_card.md).

### Truy vấn đến từ đâu? Có phải log thật không?

Không. Truy vấn do nhóm soạn từ ba corpus OpenStax, mỗi truy vấn trả lời được
bằng nội dung corpus tương ứng. Đây là giới hạn đã biết: truy vấn thật thường
lộn xộn, sai chính tả và mơ hồ hơn nhiều.

### Có thể thêm miền mới không?

Được, và không phải sửa nhiều: đặt `corpus/<slug>.txt` và
`datasets/dataset_<slug>.json`, rồi khai báo trong `DOMAIN_BY_SLUG` tại
`tools/dra_utils.py`. Split, thống kê và leave-one-domain-out tự bắt được miền
mới. Xem [../CONTRIBUTING.md](../CONTRIBUTING.md).

### Vì sao không có nhãn cho "cần truy hồi" và "cần tính toán" riêng?

Vì DRA phiên bản đang nghiên cứu chỉ có hai nhánh. Chuyển sang nhiều nhánh là
thay đổi phá vỡ tương thích, đã ghi trong [../ROADMAP.md](../ROADMAP.md).

## Về mã nguồn

### Vì sao không dùng scikit-learn?

Đánh đổi có chủ ý. Mã dài hơn, nhưng người phản biện bài báo có thể `git clone`
rồi chạy ngay trên máy trống, không vướng phiên bản numpy, wheel không build
được, hay môi trường ảo. Với quy mô 1.008 mẫu, hiệu năng thư viện chuẩn là quá
đủ: toàn bộ pipeline chạy dưới 30 giây.

Nếu bạn muốn so sánh với scikit-learn, hãy làm trong một nhánh riêng và giữ
baseline thư viện chuẩn làm mốc đối chiếu.

### Vì sao gradient descent toàn batch mà không phải SGD?

Vì tính tất định. SGD phụ thuộc thứ tự duyệt mẫu, nên hai lần chạy có thể cho
trọng số khác nhau. Toàn batch cho ra kết quả giống hệt từng byte trên mọi máy —
điều kiện cần để `--check` trong CI có nghĩa.

### Vì sao không có notebook Jupyter?

Notebook lưu kèm output và số thứ tự cell, nên diff kém và dễ commit trạng thái
không tái lập được. Mọi phân tích trong kho này đều là script sinh ra file có
thể diff được. Nếu cần khám phá dữ liệu tương tác, hãy dùng
`datasets/exports/dra_queries_all.csv` trong notebook cục bộ, đừng commit vào kho.

### Vì sao hình vẽ là SVG chứ không phải PNG?

SVG là vector nên không vỡ khi phóng to trong bản in, và là văn bản thuần nên
`git diff` xem được thay đổi. Sinh bằng `tools/make_figures.py`, không cần
matplotlib.

### Chạy test thế nào?

```bash
python -m unittest discover -s tests -v     # thư viện chuẩn
pytest tests                                 # nếu bạn có pytest
```

## Về kết quả

### Accuracy 0,97 có phải quá cao đến mức đáng ngờ không?

Đáng để hoài nghi, và chúng tôi đã kiểm tra. Không có rò rỉ giữa train và test:
split rời nhau theo `id`, từ vựng và `idf` chỉ ước lượng trên tập huấn luyện
của từng fold, và không có truy vấn trùng lặp nào trong toàn bộ dữ liệu.

Lời giải thích thật sự đơn giản hơn: truy vấn do nhóm soạn nên khuôn mẫu bề mặt
khá đều — nhãn `0` hay bắt đầu bằng `what is`, nhãn `1` hay bắt đầu bằng
`how does ... compare`. Vì vậy hãy xem con số này là **mốc sàn**, không phải bài
kiểm tra khó. Một luật độ dài đơn thuần đã đạt 0,907, cho thấy nhiệm vụ vốn dễ.

### Leave-one-domain-out gần bằng in-domain có bất thường không?

Không, và đó là kết quả thú vị nhất của kho. Các đặc trưng có trọng số lớn nhất
đều là dấu hiệu cấu trúc (`compare`, `how does`, `what is`, `how many`, nhóm độ
dài) chứ không phải thuật ngữ chuyên ngành, nên mô hình chuyển miền được. Chi
tiết trong [experiments.md](experiments.md).

### Có thể dùng kết quả này để tuyên bố DRA tiết kiệm chi phí bao nhiêu không?

Chưa. Kho này chỉ đo **chất lượng quyết định định tuyến**, không đo chi phí thật
của hai nhánh trả lời. Muốn tuyên bố về tiết kiệm chi phí thì cần thêm mô hình
chi phí cho từng nhánh và phân bố truy vấn thật — cả hai đều chưa có.

## Về giấy phép và trích dẫn

### Giấy phép nào áp dụng cho phần nào?

Mã nguồn và tài liệu: MIT (xem `LICENSE`). Corpus trong `corpus/`: trích từ sách
giáo khoa OpenStax theo **CC BY 4.0**, yêu cầu ghi công OpenStax khi phát tán
lại. Chi tiết trong [dataset_card.md](dataset_card.md).

### Trích dẫn thế nào?

Xem [../CITATION.cff](../CITATION.cff). GitHub tự sinh khối BibTeX từ file này ở
nút "Cite this repository".

### Đã có DOI chưa?

Chưa. Các bước để cấp DOI qua Zenodo nằm trong
[reproducibility.md](reproducibility.md).
