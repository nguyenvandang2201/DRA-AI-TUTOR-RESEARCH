# Thuật toán baseline định tuyến

Đặc tả đầy đủ của bộ phân loại trong
[../tools/baseline_router.py](../tools/baseline_router.py), đủ chi tiết để cài
lại từ đầu bằng ngôn ngữ khác.

Ký hiệu: $q$ là truy vấn, $y \in \{0, 1\}$ là nhãn định tuyến, $N$ là số truy
vấn huấn luyện, $V$ là tập đặc trưng.

## 1. Tách token

```text
tokenize(text) = findall(/[a-z0-9]+('[a-z]+)?/, NFKC(text).lower())
```

Chuẩn hoá NFKC ở đây là an toàn vì kết quả chỉ dùng làm đặc trưng, không ghi
ngược vào dữ liệu. Dạng rút gọn được giữ nguyên (`doesn't` là một token) vì
`n't` mang thông tin phủ định.

## 2. Tập đặc trưng

Với mỗi truy vấn, đếm ba nhóm đặc trưng:

1. **Unigram và bigram** trên chuỗi token.
2. **Nhóm độ dài** `__len_bucket_k` với $k = \min(\lfloor |tokens| / 8 \rfloor, 6)$.
3. **Số dấu hỏi** `__q_marks_m` với $m = \min(\text{count}(q, \text{"?"}), 3)$.

Hai nhóm sau được thêm có chủ đích. Thống kê cho thấy độ dài là tín hiệu định
tuyến mạnh; mã hoá nó thành đặc trưng rời rạc cho phép mô hình dùng tín hiệu đó
**phi tuyến** (mỗi nhóm có trọng số riêng) thay vì buộc quan hệ tuyến tính theo
số token.

Đặc trưng có tần suất tài liệu $< 2$ trong tập huấn luyện bị loại (`min_df = 2`),
cắt phần lớn từ chỉ xuất hiện một lần và giữ kích thước từ vựng khoảng 2.900 với
708 truy vấn huấn luyện.

## 3. Trọng số TF-IDF

Với đặc trưng $t$ trong truy vấn $q$:

$$
\text{tf}(t, q) = 1 + \log\big(\text{count}(t, q)\big)
$$

$$
\text{idf}(t) = \log\frac{1 + N}{1 + \text{df}(t)} + 1
$$

$$
x_t = \text{tf}(t, q) \cdot \text{idf}(t), \qquad
\mathbf{x} \leftarrow \frac{\mathbf{x}}{\lVert \mathbf{x} \rVert_2}
$$

Cộng 1 ở tử và mẫu của idf để đặc trưng xuất hiện trong mọi tài liệu vẫn có
trọng số dương thay vì bị triệt tiêu. Chuẩn hoá L2 khiến truy vấn dài không tự
động có chuẩn vector lớn hơn — tín hiệu độ dài đi qua `__len_bucket` chứ không
đi lén qua độ lớn vector.

**Quan trọng:** `df` và từ vựng chỉ được ước lượng trên tập huấn luyện của từng
fold. Đặc trưng chưa từng thấy trong tập kiểm tra bị bỏ qua. Đây là điểm dễ rò
rỉ thông tin nhất khi cài lại.

## 4. Mô hình

Hồi quy logistic:

$$
P(y = 1 \mid \mathbf{x}) = \sigma(\mathbf{w}^\top \mathbf{x} + b),
\qquad \sigma(z) = \frac{1}{1 + e^{-z}}
$$

Hàm mất mát là log-loss cộng phạt L2:

$$
\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N}
\Big[ y_i \log p_i + (1 - y_i) \log (1 - p_i) \Big]
+ \frac{\lambda}{2} \lVert \mathbf{w} \rVert_2^2
$$

Huấn luyện bằng **gradient descent toàn batch**:

```text
lặp E lần:
    g   ← 0,  g_b ← 0
    với mỗi (x_i, y_i):
        e   ← σ(w·x_i + b) − y_i
        g_b ← g_b + e
        với mỗi (j, v) khác 0 trong x_i:
            g_j ← g_j + e·v
    b ← b − (η/N)·g_b
    với mỗi j có g_j ≠ 0:
        w_j ← w_j − (η/N)·g_j − η·λ·w_j
```

Siêu tham số mặc định: $\eta = 2{,}0$, $E = 400$, $\lambda = 10^{-4}$.
Ngưỡng quyết định 0,5.

Chọn toàn batch thay vì SGD **không** vì hiệu năng mà vì tính tất định: không có
thứ tự duyệt mẫu nào ảnh hưởng kết quả, nên hai lần chạy trên hai máy cho ra
trọng số giống hệt nhau.

### Cài đặt thưa

Vector đặc trưng được lưu bằng `dict[int, float]` chỉ chứa phần tử khác 0. Truy
vấn trung bình có vài chục đặc trưng khác 0 trên từ vựng ~2.900, nên mỗi epoch
tốn $O(N \cdot \text{nnz})$ chứ không phải $O(N \cdot |V|)$. Toàn bộ báo cáo
(hold-out + 5-fold + 3 lần LODO) chạy khoảng 17 giây trên CPU thông thường.

Cập nhật phạt L2 chỉ áp cho toạ độ có gradient khác 0 trong epoch đó. Đây là xấp
xỉ lười của L2 đầy đủ; với 400 epoch và dữ liệu dày đặc từ chức năng thì hầu hết
toạ độ đều được chạm thường xuyên, và $\lambda$ nhỏ nên khác biệt không đáng kể.

## 5. Baseline đối chứng

| Baseline | Quy tắc | Mục đích |
| --- | --- | --- |
| `majority` | Luôn trả nhãn phổ biến nhất trong tập huấn luyện | Mức sàn tuyệt đối (0,5 vì dữ liệu cân bằng) |
| `keyword` | Trả 1 nếu truy vấn chứa từ trong `ANALYTICAL_CUES` | Bao nhiêu phần giải được bằng luật viết tay |
| `length>=k` | Trả 1 nếu số token $\ge k$; $k$ chọn bằng quét vét cạn tối ưu accuracy **trên tập huấn luyện** | Bao nhiêu phần chỉ là độ dài |

Baseline độ dài là đối chứng quan trọng nhất. Nếu mô hình đầy đủ không vượt rõ
nó, nghĩa là bộ dữ liệu chỉ đang đo lại độ dài câu hỏi.

## 6. Chỉ số đánh giá

Với `tp`, `tn`, `fp`, `fn` tính theo nhãn dương là 1:

$$
\text{accuracy} = \frac{tp + tn}{n}, \quad
\text{precision} = \frac{tp}{tp + fp}, \quad
\text{recall} = \frac{tp}{tp + fn}
$$

$$
F_1 = \frac{2 \cdot \text{precision} \cdot \text{recall}}
           {\text{precision} + \text{recall}}, \qquad
\text{macro-}F_1 = \frac{F_1^{(0)} + F_1^{(1)}}{2}
$$

Mẫu số bằng 0 được quy ước cho ra 0, không phải lỗi chia. Vì dữ liệu cân bằng,
accuracy và macro-F1 gần nhau; chênh lệch giữa hai chỉ số là dấu hiệu mô hình
thiên lệch về một nhãn.

## 7. Chi phí định tuyến

Điểm mấu chốt với DRA: suy luận cho một truy vấn là một lần tách token, một lần
tra dict và một tích vô hướng thưa — dưới một mili-giây, không cấp phát bộ nhớ
lớn, không gọi mạng. Chi phí này nhỏ hơn nhiều bậc so với bất kỳ lần gọi mô hình
ngôn ngữ nào mà nó giúp tránh, nên gần như toàn bộ phần tiết kiệm được của việc
định tuyến đúng đều được giữ lại.
