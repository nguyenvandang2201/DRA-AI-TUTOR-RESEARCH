# Hướng dẫn gán nhãn

Tài liệu này định nghĩa nhãn `label` trong `datasets/*.json` đủ chặt để hai
người gán nhãn độc lập cho ra kết quả giống nhau. Mọi bản ghi mới phải theo đúng
quy trình dưới đây.

## Nhãn dùng trong dự án

| Nhãn | Tên gọi | Ý nghĩa định tuyến trong DRA |
| ---: | --- | --- |
| `0` | factual | Trả lời được bằng tra cứu trực tiếp hoặc nhắc lại một sự kiện, định nghĩa, công thức, con số có sẵn trong corpus. Định tuyến sang nhánh rẻ (mô hình nhỏ + truy hồi). |
| `1` | analytical | Cần suy luận nhiều bước: so sánh, tổng hợp nhiều nguồn/chương, giải thích cơ chế nhân quả, đánh giá. Định tuyến sang nhánh suy luận sâu (mô hình lớn). |

Nhãn mô tả **loại công việc mà truy vấn đòi hỏi**, không mô tả độ dài câu hỏi
hay độ khó chủ quan với một người học cụ thể.

## Quy tắc quyết định

Áp dụng theo thứ tự, dừng ở quy tắc đầu tiên khớp:

1. **Một sự kiện tra được** -> `0`.
   Câu trả lời đúng nằm gọn trong một đoạn văn/bảng của corpus, không cần biến đổi.
   *Ví dụ:* "In what year was the Triple Entente formally created?"

2. **Định nghĩa hoặc công thức được nêu thẳng** -> `0`.
   Kể cả khi thuật ngữ mang tính kỹ thuật cao.
   *Ví dụ:* "What is the formula for calculating a z-score?"

3. **Liệt kê các mục đã được liệt kê sẵn trong sách** -> `0`.
   *Ví dụ:* "What are the four main characteristics of a perfectly competitive market?"

4. **So sánh, đối chiếu, hoặc bắc cầu giữa hai khái niệm/chương** -> `1`.
   *Ví dụ:* "How does the zero-profit point compare to the shutdown point?"

5. **Hỏi cơ chế nhân quả, hệ quả, hoặc tương tác nhiều yếu tố** -> `1`.
   *Ví dụ:* "How do changes in technology, policy, and preferences interact to
   reshape equilibrium price?"

6. **Yêu cầu đánh giá, nhận định, hoặc rút ra hàm ý** -> `1`.
   *Ví dụ:* "What does this formula reveal about the relationship between spread
   and slope?"

## Trường hợp ranh giới

| Tình huống | Nhãn | Lý do |
| --- | ---: | --- |
| "What was the Yalta Conference, and what were its three main outcomes?" | `0` | Hai vế nhưng cả hai đều tra trực tiếp; ghép câu không tạo ra suy luận. |
| "Why did the Schlieffen Plan fail?" nếu sách nêu thẳng nguyên nhân | `0` | Từ "why" không tự động thành `1`; điều quyết định là câu trả lời có sẵn hay phải suy ra. |
| "How many children did the Kindertransport rescue?" | `0` | "How" ở đây là hỏi số lượng. |
| "Compare X and Y" khi sách có sẵn một bảng so sánh X-Y | `1` | Người học vẫn phải chọn tiêu chí và diễn giải; giữ `1` cho nhất quán với các truy vấn so sánh khác. |
| Câu hỏi có hai dấu hỏi, vế sau là "and why?" | `1` | Vế "why" đẩy truy vấn sang suy luận. |
| Truy vấn có bối cảnh cá nhân ("I don't understand...") | theo nội dung | Bỏ phần cảm thán, gán nhãn theo câu hỏi thực sự. |

Đừng dùng độ dài làm tiêu chí. Độ dài chỉ tương quan với nhãn (xem
[dataset_stats.md](dataset_stats.md)), nó không phải là định nghĩa; gán nhãn
theo độ dài sẽ làm bộ dữ liệu chỉ còn đo lại chính heuristic độ dài.

## Quy trình gán nhãn

1. Rút truy vấn từ corpus của đúng miền; mỗi truy vấn phải trả lời được từ corpus.
2. Gán nhãn theo quy tắc trên, ghi lại quy tắc số mấy đã áp dụng nếu còn phân vân.
3. Giữ cân bằng: mỗi file nhắm tỉ lệ nhãn `0`/`1` xấp xỉ 50/50
   (`tools/validate_datasets.py` cảnh báo khi lệch quá 10%).
4. Chạy `python tools/validate_datasets.py --strict` trước khi commit.
5. Sinh lại các file dẫn xuất: `python tools/make_splits.py`,
   `python tools/dataset_stats.py`, `python tools/export_dataset.py`.

## Đo độ đồng thuận giữa người gán nhãn

Khi bổ sung một lô dữ liệu mới, nên để người thứ hai gán lại độc lập ít nhất
50 truy vấn và báo cáo Cohen's kappa trong `docs/research_log.md`.

Với hai người gán nhãn trên nhãn nhị phân, kappa tính như sau:

```text
p_o     = tỉ lệ bản ghi hai người gán giống nhau
p_e     = P(cả hai gán 0) + P(cả hai gán 1), tính từ tỉ lệ biên của từng người
kappa   = (p_o - p_e) / (1 - p_e)
```

Mốc tham chiếu thường dùng: `kappa >= 0.80` là đồng thuận tốt cho nhãn nhị phân.
Nếu thấp hơn, bổ sung trường hợp gây tranh cãi vào bảng "Trường hợp ranh giới"
ở trên rồi gán lại, thay vì tự ý sửa nhãn cho khớp.

## Điều cần tránh

- **Rò rỉ đáp án giữa các split.** Không tạo hai truy vấn chỉ khác nhau cách diễn
  đạt; công cụ kiểm định bắt trùng lặp chính xác nhưng không bắt được diễn giải lại.
- **Nhãn theo miền.** Không mặc định truy vấn Thống kê là `1` vì "toán khó hơn".
- **Truy vấn không trả lời được từ corpus.** Nếu đáp án không nằm trong corpus,
  loại truy vấn đó thay vì đoán nhãn.
