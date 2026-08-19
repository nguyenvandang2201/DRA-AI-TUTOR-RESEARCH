## Tóm tắt

<!-- Thay đổi gì, và vì sao. Một hai câu là đủ. -->

## Loại thay đổi

- [ ] Dữ liệu (`datasets/`, `corpus/`)
- [ ] Công cụ (`tools/`)
- [ ] Kiểm thử (`tests/`)
- [ ] Tài liệu
- [ ] CI / cấu hình kho

## Kiểm tra trước khi gửi

- [ ] `python tools/validate_datasets.py --strict` không còn lỗi lẫn cảnh báo
- [ ] `python -m unittest discover -s tests -v` toàn bộ pass
- [ ] Đã sinh lại file dẫn xuất và commit kèm (`make all` hoặc `./tasks.ps1 all`)
- [ ] `git status` sạch sau khi sinh lại
- [ ] Đã ghi một dòng vào `docs/research_log.md` (nếu thay đổi dữ liệu)
- [ ] Đã cập nhật `CHANGELOG.md`

## Nếu thay đổi dữ liệu

- [ ] Gán nhãn theo `docs/labeling_guidelines.md`; nêu rõ quy tắc đã áp dụng cho
      các trường hợp gây tranh cãi
- [ ] Cân bằng nhãn của file vẫn trong ngưỡng 10%
- [ ] Mọi truy vấn mới đều trả lời được từ corpus tương ứng

<!--
Lưu ý: file dẫn xuất (datasets/splits, datasets/exports, docs/dataset_stats.md,
docs/baseline_results.md, results/, figures/) được sinh tự động. Đừng sửa tay;
CI sẽ fail nếu chúng lệch khỏi dữ liệu nguồn.
-->
