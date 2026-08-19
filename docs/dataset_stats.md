# Thống kê bộ dữ liệu

File này được sinh tự động bởi `python tools/dataset_stats.py`.
Đừng sửa tay: hãy chạy lại script sau khi thay đổi dữ liệu.

## Tổng quan

| File | Domain | Bản ghi | Nhãn 0 | Nhãn 1 | Tỷ lệ nhãn 1 |
| --- | --- | ---: | ---: | ---: | ---: |
| `dataset_introductory_statistics.json` | Introductory Statistics | 336 | 168 | 168 | 50.0% |
| `dataset_microeconomics.json` | Microeconomics | 336 | 168 | 168 | 50.0% |
| `dataset_world_history.json` | World History | 336 | 168 | 168 | 50.0% |
| **Tổng** | - | 1008 | 504 | 504 | 50.0% |

## Độ dài truy vấn theo miền và nhãn

Độ dài tính bằng token (tách theo `dra_utils.tokenize`).

| Domain | Nhãn | n | Token TB | Trung vị | Min-Max | Ký tự TB | Nhiều dấu hỏi |
| --- | --- | ---: | ---: | ---: | :---: | ---: | ---: |
| Introductory Statistics | 0 (factual) | 168 | 14.5 | 14 | 4-28 | 82 | 0.0% |
| Introductory Statistics | 1 (analytical) | 168 | 35.8 | 35 | 13-66 | 228 | 13.1% |
| Microeconomics | 0 (factual) | 168 | 13.0 | 13 | 4-24 | 73 | 0.0% |
| Microeconomics | 1 (analytical) | 168 | 25.6 | 25 | 9-46 | 165 | 0.0% |
| World History | 0 (factual) | 168 | 14.5 | 15 | 7-23 | 83 | 0.0% |
| World History | 1 (analytical) | 168 | 26.9 | 26 | 16-46 | 177 | 6.5% |

Khoảng cách độ dài giữa hai nhãn là tín hiệu định tuyến rẻ nhất: truy vấn
analytical dài hơn đáng kể vì thường ghép nhiều mệnh đề so sánh hoặc giải thích.

## Từ mở đầu truy vấn

| Từ mở đầu | Nhãn 0 | Nhãn 1 | Tổng |
| --- | ---: | ---: | ---: |
| `what` | 321 | 13 | 334 |
| `how` | 43 | 251 | 294 |
| `(khác)` | 129 | 95 | 224 |
| `compare` | 0 | 115 | 115 |
| `analyze` | 0 | 19 | 19 |
| `explain` | 0 | 11 | 11 |
| `define` | 9 | 0 | 9 |
| `when` | 1 | 0 | 1 |
| `who` | 1 | 0 | 1 |

## Từ khoá phân biệt nhãn

Điểm log-odds (làm mượt Laplace) trên tần suất tài liệu; điểm dương nghiêng
về nhãn 1, điểm âm nghiêng về nhãn 0.

| Token | Log-odds | Truy vấn nhãn 1 | Truy vấn nhãn 0 |
| --- | ---: | ---: | ---: |
| `compare` | +4.08 | 191 | 1 |
| `explain` | +3.95 | 83 | 0 |
| `synthesize` | +3.39 | 47 | 0 |
| `concepts` | +3.37 | 46 | 0 |
| `together` | +3.21 | 39 | 0 |
| `would` | +2.95 | 30 | 0 |
| `these` | +2.92 | 29 | 0 |
| `or` | +2.74 | 24 | 0 |
| `using` | +2.74 | 49 | 1 |
| `both` | +2.71 | 72 | 2 |
| `interact` | +2.65 | 22 | 0 |
| `analyze` | +2.61 | 21 | 0 |
| `according` | -3.66 | 0 | 23 |
| `economics` | -3.37 | 0 | 17 |
| `many` | -3.37 | 2 | 53 |
| `table` | -3.26 | 1 | 31 |
| `8` | -3.19 | 0 | 14 |
| `was` | -3.02 | 5 | 75 |
| `healthpill's` | -2.97 | 0 | 11 |
| `microeconomics` | -2.97 | 0 | 11 |
| `farm` | -2.88 | 0 | 10 |
| `raspberry` | -2.88 | 0 | 10 |
| `date` | -2.79 | 0 | 9 |
| `q` | -2.68 | 0 | 8 |

## Corpus tham chiếu

| File | Dòng | Token | Kích thước |
| --- | ---: | ---: | ---: |
| `introductory_statistics.txt` | 4,744 | 33,106 | 176 KB |
| `microeconomics.txt` | 3,999 | 40,428 | 227 KB |
| `world_history.txt` | 3,197 | 44,684 | 263 KB |

## Trùng lặp

- Truy vấn duy nhất: 1,008 / 1,008
- Nhóm truy vấn trùng lặp (sau chuẩn hoá): 0
