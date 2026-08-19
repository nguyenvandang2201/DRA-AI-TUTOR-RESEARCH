# Kết quả baseline định tuyến

File này được sinh tự động bởi `python tools/baseline_router.py --report`.
Mô hình chỉ dùng thư viện chuẩn Python nên số liệu lặp lại được trên máy trống.

Nhiệm vụ: dự đoán nhãn định tuyến của truy vấn (0 = factual, 1 = analytical).
Cấu hình: TF-IDF 1-2 gram, min_df=2, hồi quy logistic (GD toàn batch, 400 epoch, L2=1e-4).

## 1. Hold-out (train -> test)

Huấn luyện trên `datasets/splits/train.json`, đánh giá trên `datasets/splits/test.json`.

| Mô hình | Accuracy | Precision | Recall | F1 | Macro-F1 | TP/FP/FN/TN |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| tfidf+logreg | 0.973 | 0.986 | 0.960 | 0.973 | 0.973 | 72/1/3/74 |
| length>=19 | 0.907 | 0.918 | 0.893 | 0.905 | 0.907 | 67/6/8/69 |
| keyword | 0.887 | 0.822 | 0.987 | 0.897 | 0.886 | 74/16/1/59 |
| majority | 0.500 | 0.000 | 0.000 | 0.000 | 0.333 | 0/0/75/75 |

## 2. Kiểm định chéo 5-fold phân tầng (toàn bộ 1008 truy vấn)

| Chỉ số | Trung bình |
| --- | ---: |
| Accuracy | 0.983 ± 0.011 |
| Precision (nhãn 1) | 0.984 |
| Recall (nhãn 1) | 0.982 |
| F1 (nhãn 1) | 0.983 |
| Macro-F1 | 0.983 |

Accuracy từng fold: 0.966, 0.985, 0.990, 0.980, 0.995.

## 3. Leave-one-domain-out

Huấn luyện trên hai miền, đánh giá trên miền chưa từng thấy. Đây là phép đo
khả năng khái quát hoá liên miền của tầng định tuyến.

| Miền dùng để test | Accuracy | Precision | Recall | F1 | Macro-F1 | TP/FP/FN/TN |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| World History | 0.988 | 0.982 | 0.994 | 0.988 | 0.988 | 167/3/1/165 |
| Microeconomics | 0.985 | 0.988 | 0.982 | 0.985 | 0.985 | 165/2/3/166 |
| Introductory Statistics | 0.955 | 0.969 | 0.940 | 0.955 | 0.955 | 158/5/10/163 |

## 4. Đặc trưng có trọng số lớn nhất

Trọng số dương đẩy truy vấn về nhãn 1 (analytical), trọng số âm về nhãn 0 (factual).

| Đẩy về nhãn 1 | Trọng số | Đẩy về nhãn 0 | Trọng số |
| --- | ---: | --- | ---: |
| `compare` | +3.347 | `__len_bucket_1` | -4.920 |
| `__len_bucket_3` | +2.215 | `what` | -4.879 |
| `__q_marks_0` | +2.143 | `what is` | -4.141 |
| `compare the` | +2.031 | `is` | -3.874 |
| `__len_bucket_4` | +1.908 | `__q_marks_1` | -2.863 |
| `how` | +1.883 | `is the` | -2.652 |
| `how does` | +1.841 | `it` | -2.262 |
| `of` | +1.822 | `was` | -2.145 |
| `with` | +1.561 | `how many` | -2.112 |
| `compare to` | +1.504 | `many` | -2.066 |

## Diễn giải

- Baseline luật (`majority`, `keyword`, `length`) cho biết mức sàn: phần nào của
  nhiệm vụ giải được chỉ bằng heuristic không cần học.
- Khoảng cách giữa hold-out và leave-one-domain-out cho biết router học đặc trưng
  cấu trúc câu hỏi (khái quát được) hay chỉ học từ vựng riêng của từng miền.
- Mọi kết quả cao hơn ở đây đều nên được so với chi phí: baseline này chạy dưới
  một mili-giây cho mỗi truy vấn và không cần gọi API.
