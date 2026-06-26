# DRA AI Tutor Research

Kho lưu trữ này chứa tài liệu nghiên cứu, bộ dữ liệu và corpus phục vụ đề tài
Dynamic Routing Architecture (DRA) cho hệ thống AI gia sư. Mục tiêu của dự án
là hỗ trợ đánh giá định tuyến truy vấn theo mức độ phức tạp và miền kiến thức.

## Cấu trúc thư mục

```text
dra-ai-tutor-research/
├── paper/      # Bản thảo bài báo PDF/DOCX
├── datasets/   # Bộ dữ liệu truy vấn đã gán nhãn
├── corpus/     # Nguồn văn bản tham chiếu theo từng miền
└── docs/       # Tài liệu mô tả dữ liệu và quy trình
```

## Nội dung chính

- `paper/DRA_AI_Tutor_Paper.pdf`: bản PDF của bài báo nghiên cứu.
- `paper/DRA_AI_Tutor_Paper.docx`: bản Word có thể chỉnh sửa.
- `datasets/*.json`: các bộ dữ liệu theo miền World History, Microeconomics và
  Introductory Statistics.
- `corpus/*.txt`: nguồn văn bản dùng để đối chiếu hoặc xây dựng truy vấn.
- `docs/dataset_description.md`: mô tả schema, quy ước nhãn và cách kiểm tra dữ
  liệu.

## Kiểm tra dữ liệu

Chạy lệnh sau trong PowerShell để xác nhận toàn bộ file JSON hợp lệ:

```powershell
Get-ChildItem datasets/*.json | ForEach-Object { Get-Content -Raw $_ | ConvertFrom-Json > $null }
```

Để xem nhanh số lượng bản ghi và nhãn:

```powershell
Get-ChildItem datasets/*.json | ForEach-Object {
  $json = Get-Content -Raw $_ | ConvertFrom-Json
  $json | Group-Object label
}
```

## Ghi chú đóng góp

Khi thêm dữ liệu mới, giữ đúng schema `query`, `domain`, `label`; đặt tên file
theo dạng `dataset_<domain>.json`; và cập nhật tài liệu trong `docs/` nếu thay
đổi quy ước nhãn, nguồn corpus hoặc phương pháp tạo dữ liệu.
