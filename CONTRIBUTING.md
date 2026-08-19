# Hướng dẫn đóng góp

Cảm ơn bạn đã đóng góp cho kho nghiên cứu DRA AI Tutor. Tài liệu này mô tả quy
trình tối thiểu để thay đổi được chấp nhận.

## Yêu cầu môi trường

Chỉ cần **Python 3.9 trở lên**. Toàn bộ công cụ trong `tools/` dùng thư viện
chuẩn, không có dependency và không cần virtualenv.

## Vòng lặp làm việc

```powershell
# Windows PowerShell
./tasks.ps1 all      # sinh lại mọi file dẫn xuất rồi chạy test
./tasks.ps1 check    # kiểm tra mọi thứ đã cập nhật (giống CI)
```

```bash
# macOS / Linux
make all
make check
```

## Khi thay đổi dữ liệu trong `datasets/`

Ba file `datasets/dataset_*.json` là **nguồn sự thật duy nhất**. Mọi thứ khác
được sinh ra từ chúng.

1. Sửa file dataset, giữ đúng schema `query` / `domain` / `label`
   (đúng ba trường, không thêm bớt).
2. Gán nhãn theo [docs/labeling_guidelines.md](docs/labeling_guidelines.md).
3. Chạy `python tools/validate_datasets.py --strict` cho tới khi không còn cảnh báo.
4. Sinh lại file dẫn xuất và commit kèm:

   ```
   python tools/make_splits.py
   python tools/dataset_stats.py
   python tools/export_dataset.py
   python tools/baseline_router.py --report   # nếu muốn cập nhật số liệu baseline
   ```

5. Ghi một dòng vào [docs/research_log.md](docs/research_log.md).

CI sẽ fail nếu file dẫn xuất không khớp dữ liệu nguồn, nên bước 4 là bắt buộc.

## Khi thêm một miền mới

1. Đặt corpus vào `corpus/<slug>.txt`.
2. Đặt dataset vào `datasets/dataset_<slug>.json`.
3. Khai báo ánh xạ trong `DOMAIN_BY_SLUG` tại
   [tools/dra_utils.py](tools/dra_utils.py) -- thiếu bước này, validator sẽ cảnh báo.
4. Cập nhật [docs/dataset_card.md](docs/dataset_card.md).

## Khi sửa code trong `tools/`

- Giữ nguyên nguyên tắc **không dependency ngoài thư viện chuẩn**.
- Mọi thứ phải tất định: sắp xếp trước khi trộn, seed tường minh, phá hoà bằng
  khoá phụ. Test `test_splits_are_reproducible` bảo vệ điều này.
- Thêm test vào [tests/test_datasets.py](tests/test_datasets.py) cho hành vi mới.
- Chú thích và docstring viết bằng tiếng Việt cho thống nhất với phần còn lại.

## Không commit vào kho

- File dẫn xuất chưa được sinh lại (sẽ lệch với dữ liệu nguồn).
- File tạm của Office (`~$*.docx`), cache Python, thư mục IDE -- đã có trong `.gitignore`.
- Dữ liệu cá nhân của người học hoặc log truy vấn thật chưa được ẩn danh.

## Quy ước commit

Dùng tiền tố kiểu Conventional Commits, phần mô tả bằng tiếng Việt:

```
feat: thêm 40 truy vấn miền Microeconomics
fix: sửa nhãn sai ở dataset_world_history.json
docs: cập nhật hướng dẫn gán nhãn cho trường hợp ranh giới
chore: sinh lại file dẫn xuất sau khi đổi seed
```
