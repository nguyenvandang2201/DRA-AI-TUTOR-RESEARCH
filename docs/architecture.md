# Kiến trúc

Tài liệu này mô tả hai thứ: vị trí của bộ dữ liệu trong kiến trúc DRA mà nó phục
vụ, và cách kho được tổ chức để giữ tính tái lập.

## 1. Vị trí của bộ dữ liệu trong DRA

Dynamic Routing Architecture đặt một **tầng định tuyến** trước các nhánh trả lời
có chi phí khác nhau:

```text
                    ┌──────────────────────────────┐
   Truy vấn của     │      TẦNG ĐỊNH TUYẾN         │
   người học  ─────>│  phân loại độ phức tạp       │
                    │  (đối tượng của kho này)     │
                    └───────────┬──────────────────┘
                                │
              nhãn 0            │            nhãn 1
        (factual)               │        (analytical)
                ┌───────────────┴───────────────┐
                v                               v
   ┌──────────────────────────┐   ┌──────────────────────────────┐
   │  NHÁNH TRA CỨU NHANH     │   │  NHÁNH SUY LUẬN SÂU          │
   │  truy hồi + mô hình nhỏ  │   │  mô hình lớn, nhiều bước     │
   │  độ trễ thấp, chi phí rẻ │   │  độ trễ cao, chi phí lớn     │
   └────────────┬─────────────┘   └───────────────┬──────────────┘
                └───────────────┬────────────────-┘
                                v
                        Câu trả lời cho người học
```

Kho này **không cài đặt hai nhánh trả lời**. Nó cung cấp dữ liệu và mốc so sánh
cho đúng một quyết định: nhánh nào nên nhận truy vấn.

Điều đó dẫn tới ràng buộc thiết kế quan trọng: bộ định tuyến chỉ có giá trị nếu
nó **rẻ hơn nhiều so với nhánh mà nó tránh được**. Một router phải gọi LLM để
quyết định có nên gọi LLM hay không thì vô nghĩa. Vì vậy baseline trong
[../tools/baseline_router.py](../tools/baseline_router.py) cố tình dùng mô hình
tuyến tính chạy dưới một mili-giây, không gọi mạng.

## 2. Luồng dữ liệu trong kho

```text
  corpus/*.txt                 (nguồn OpenStax, CC BY 4.0)
       │
       │  soạn truy vấn thủ công theo docs/labeling_guidelines.md
       v
  datasets/dataset_<domain>.json          ← NGUỒN SỰ THẬT DUY NHẤT
       │
       ├── tools/validate_datasets.py ──> pass / fail (CI chặn ở đây)
       │
       ├── tools/make_splits.py ────────> datasets/splits/{train,dev,test}.json
       │                                  datasets/splits/manifest.json
       │
       ├── tools/dataset_stats.py ──────> docs/dataset_stats.md
       │
       ├── tools/export_dataset.py ─────> datasets/exports/*.{csv,jsonl}
       │
       └── tools/baseline_router.py ────> docs/baseline_results.md
                    │                     results/baseline_metrics.json
                    │
                    └── tools/make_figures.py ──> figures/*.svg
```

Mọi mũi tên đều một chiều. Không có script nào ghi ngược vào
`datasets/dataset_*.json`; sửa dữ liệu là việc thủ công, có chủ đích.

## 3. Ba nguyên tắc kiến trúc

### 3.1. Một nguồn sự thật, phần còn lại sinh lại được

Chỉ ba file dataset được sửa tay. Mọi file khác đều có script sinh ra và một cờ
`--check` để CI phát hiện khi chúng lệch khỏi nguồn. Hệ quả: không bao giờ phải
tự hỏi con số trong bài báo đến từ phiên bản dữ liệu nào.

### 3.2. Không dependency runtime

Toàn bộ `tools/` chạy bằng thư viện chuẩn Python 3.9+, kể cả TF-IDF, hồi quy
logistic và bộ sinh SVG. Đánh đổi có ý thức: mã dài hơn dùng scikit-learn,
nhưng người phản biện bài báo có thể `git clone` rồi chạy ngay, không vướng
xung đột phiên bản numpy hay wheel không build được.

Ranh giới: `ruff` và `coverage` là công cụ phát triển tuỳ chọn, khai báo trong
`requirements-dev.txt`. Chúng không bao giờ cần thiết để sinh lại kết quả.

### 3.3. Tất định tuyệt đối

Mọi chỗ có thứ tự đều được ghim:

- Sắp xếp trước khi trộn, seed tường minh cho từng tầng phân tầng.
- Phá hoà bằng khoá phụ (thường là token hoặc `id`) trong mọi phép sort.
- Duyệt tập hợp qua `sorted()`, không dựa vào thứ tự chèn.
- Huấn luyện bằng gradient descent **toàn batch**, không SGD, nên kết quả không
  phụ thuộc thứ tự duyệt mẫu.

Kiểm chứng: chạy lại với `PYTHONHASHSEED` khác nhau phải cho ra file giống hệt
từng byte. Test `test_splits_are_reproducible` giữ bất biến này.

## 4. Các thành phần chính

| Thành phần | File | Vai trò |
| --- | --- | --- |
| Tiện ích chung | `tools/dra_utils.py` | Tách token, chuẩn hoá, `id` ổn định, ghi file UTF-8/LF, bảng Markdown |
| Kiểm định | `tools/validate_datasets.py` | Cổng chất lượng, chạy đầu tiên trong CI |
| Phân chia dữ liệu | `tools/make_splits.py` | Split phân tầng theo `(domain, label)` |
| Đặc trưng | `TfidfVectorizer` trong `baseline_router.py` | TF-IDF 1-2 gram + đặc trưng cấu trúc |
| Mô hình | `LogisticRegression` trong `baseline_router.py` | Phân loại tuyến tính, GD toàn batch + L2 |
| Baseline đối chứng | `LengthBaseline`, `KeywordBaseline` | Mức sàn để biết mô hình học thêm được gì |
| Trình bày | `dataset_stats.py`, `make_figures.py` | Bảng Markdown và hình SVG cho bài báo |

Chi tiết toán học của tầng đặc trưng và mô hình nằm trong
[algorithm.md](algorithm.md); giao thức đánh giá nằm trong
[experiments.md](experiments.md).

## 5. Điểm mở rộng

- **Thêm miền:** đặt corpus và dataset theo quy ước tên, khai báo trong
  `DOMAIN_BY_SLUG`. Không phải sửa gì khác; split, thống kê và LODO tự bắt được
  miền mới.
- **Thêm mô hình:** cài lớp có `fit`/`predict` rồi thêm vào `evaluate_rules` hoặc
  `compute_all`. Hàm `metrics` và bộ đo dùng chung.
- **Đổi số nhánh định tuyến:** đây là thay đổi phá vỡ tương thích. Nó chạm vào
  `VALID_LABELS`, `LABEL_NAMES`, phân tầng split và mọi công thức đo nhị phân —
  xem [../ROADMAP.md](../ROADMAP.md).
