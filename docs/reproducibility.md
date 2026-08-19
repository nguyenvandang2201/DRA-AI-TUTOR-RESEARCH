# Hướng dẫn tái lập kết quả

Mọi con số trong bài báo và trong `docs/` đều sinh lại được từ ba file dataset
nguồn. Tài liệu này ghi chính xác cách làm và cách kiểm chứng.

## Yêu cầu

| Mục | Giá trị |
| --- | --- |
| Python | 3.9 trở lên (đã kiểm chứng trên 3.9, 3.11, 3.12) |
| Dependency | **không có** — toàn bộ dùng thư viện chuẩn |
| Hệ điều hành | Windows, Linux, macOS |
| Thời gian chạy | dưới 30 giây cho toàn bộ pipeline |
| Phần cứng | CPU bất kỳ; không cần GPU, không cần mạng |

## Tái lập trong bốn lệnh

```bash
git clone https://github.com/nguyenvandang2201/DRA-AI-TUTOR-RESEARCH.git
cd DRA-AI-TUTOR-RESEARCH
python tools/validate_datasets.py --strict
python -m unittest discover -s tests -v
```

Sinh lại toàn bộ file dẫn xuất:

```bash
python tools/make_splits.py
python tools/dataset_stats.py
python tools/export_dataset.py
python tools/baseline_router.py --report
python tools/make_figures.py
```

Hoặc gọn hơn: `make all` (Linux, macOS) / `./tasks.ps1 all` (Windows).

## Kiểm chứng: kết quả có thật sự tái lập không?

Cách kiểm tra mạnh nhất là sinh lại rồi xác nhận **không có gì thay đổi**:

```bash
make all          # hoặc ./tasks.ps1 all
git status        # phải sạch, không file nào bị sửa
```

Nếu `git status` báo có thay đổi, nghĩa là file dẫn xuất trong kho đã lệch khỏi
dữ liệu nguồn — đó là lỗi cần sửa, không phải chuyện bình thường.

Các cờ `--check` làm đúng việc đó mà không ghi đè file:

```bash
python tools/make_splits.py --check
python tools/dataset_stats.py --check
python tools/export_dataset.py --check
python tools/baseline_router.py --check
python tools/make_figures.py --check
```

CI chạy toàn bộ những lệnh này trên mỗi push.

## Điều gì bảo đảm tính tất định

| Nguồn ngẫu nhiên tiềm tàng | Cách xử lý |
| --- | --- |
| Thứ tự file trên đĩa | Luôn `sorted(glob(...))` |
| Thứ tự duyệt `set` và `dict` | Duyệt qua `sorted()`; không dựa vào thứ tự chèn |
| Băm chuỗi (`PYTHONHASHSEED`) | Không ảnh hưởng vì mọi tập hợp đều được sắp trước khi dùng |
| Trộn ngẫu nhiên khi chia split | `random.Random(f"{seed}:{stratum}")`, seed tường minh |
| Hoà điểm khi sắp xếp | Phá hoà bằng khoá phụ (`token`, `id`) |
| Thứ tự duyệt mẫu khi huấn luyện | Gradient descent **toàn batch**, không SGD |
| Xuống dòng theo hệ điều hành | Mọi file ghi bằng `write_text` với `newline="\n"` |
| Mã hoá ký tự | UTF-8 tường minh ở mọi thao tác đọc/ghi |

Kiểm chứng nhanh rằng băm chuỗi không ảnh hưởng:

```bash
PYTHONHASHSEED=1  python tools/dataset_stats.py --check
PYTHONHASHSEED=99 python tools/dataset_stats.py --check
```

Cả hai đều phải báo "đã cập nhật".

## Hằng số cần biết

| Hằng số | Giá trị | Nơi khai báo |
| --- | --- | --- |
| Seed chia split | `20260819` | `tools/make_splits.py` |
| Tỉ lệ train/dev/test | 0,70 / 0,15 / 0,15 | `tools/make_splits.py` |
| Số fold kiểm định chéo | 5 | `tools/baseline_router.py` |
| Số epoch | 400 | `tools/baseline_router.py` |
| Tốc độ học | 2,0 | `tools/baseline_router.py` |
| Hệ số L2 | 1e-4 | `tools/baseline_router.py` |
| `min_df` | 2 | `TfidfVectorizer` |

Seed cũng được ghi trong `datasets/splits/manifest.json` và
`results/baseline_metrics.json`, nên mỗi file kết quả tự mang theo cấu hình đã
sinh ra nó.

## Chạy trong Docker (tuỳ chọn)

Nếu muốn cô lập hoàn toàn khỏi Python trên máy:

```bash
docker build -t dra-research .
docker run --rm dra-research          # chạy toàn bộ kiểm định và test
```

## Số liệu mong đợi

Sau khi chạy lại, các con số sau phải khớp chính xác:

| Chỉ số | Giá trị |
| --- | --- |
| Tổng số bản ghi | 1.008 |
| Kích thước split | 708 / 150 / 150 |
| Hold-out accuracy (test) | 0,973 |
| Kiểm định chéo 5-fold | 0,983 ± 0,011 |
| Leave-one-domain-out | 0,955 / 0,985 / 0,988 |
| Số đặc trưng sau `min_df` | 2.926 |

Nếu lệch, hãy kiểm tra trước tiên xem `datasets/dataset_*.json` có bị sửa hay
không (`git diff datasets/`).

## Phát hành và DOI

Kho chưa có DOI. Khi cần trích dẫn cố định cho bài báo:

1. Tạo tag và GitHub Release (xem [../CONTRIBUTING.md](../CONTRIBUTING.md)).
2. Bật tích hợp Zenodo cho kho trên <https://zenodo.org/account/settings/github/>.
3. Release tiếp theo sẽ được Zenodo cấp DOI tự động.
4. Thêm DOI vào `CITATION.cff` (trường `doi`) và huy hiệu DOI vào `README.md`.

`CITATION.cff` đã sẵn sàng cho bước này; chỉ thiếu trường `doi` và, nếu có,
`orcid` của tác giả.
