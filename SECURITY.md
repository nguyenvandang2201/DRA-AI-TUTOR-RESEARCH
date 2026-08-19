# Chính sách bảo mật

## Phạm vi

Kho này là kho **dữ liệu và mã nghiên cứu**, không phải dịch vụ đang vận hành.
Nó không có endpoint mạng, không xử lý dữ liệu người dùng, không lưu thông tin
xác thực, và không có dependency runtime nào (toàn bộ `tools/` chạy bằng thư
viện chuẩn Python). Bề mặt tấn công vì vậy rất nhỏ.

Dù vậy, các vấn đề sau vẫn nằm trong phạm vi báo cáo:

- Mã trong `tools/` hoặc `tests/` thực thi nội dung không tin cậy, ghi ra ngoài
  thư mục kho, hoặc có thể bị lợi dụng khi xử lý file dataset do người khác gửi.
- Workflow trong `.github/workflows/` có quyền quá rộng, hoặc có nguy cơ bị chèn
  script qua nội dung pull request.
- Dữ liệu cá nhân hoặc thông tin nhạy cảm vô tình lọt vào `datasets/`,
  `corpus/`, hoặc lịch sử Git.
- Nội dung vi phạm bản quyền trong `corpus/` vượt quá phạm vi giấy phép CC BY 4.0.

## Cách báo cáo

Gửi email tới **ngvandang9999@gmail.com** với tiêu đề bắt đầu bằng
`[SECURITY] dra-ai-tutor-research`.

Vui lòng **không** mở issue công khai cho vấn đề bảo mật hoặc rò rỉ dữ liệu cá
nhân. Với lỗi thông thường, hãy dùng issue như bình thường.

Trong báo cáo, nếu có thể xin nêu:

- mô tả vấn đề và tác động có thể xảy ra;
- các bước tái hiện, hoặc file/dòng mã liên quan;
- phiên bản hoặc commit bạn đang xem.

## Thời gian phản hồi

Đây là dự án nghiên cứu do một người duy trì, không có cam kết SLA. Dự kiến phản
hồi trong vòng 14 ngày. Nếu vấn đề được xác nhận, bản vá sẽ đi kèm ghi chú trong
[CHANGELOG.md](CHANGELOG.md).

## Phiên bản được hỗ trợ

Chỉ nhánh `main` và bản phát hành mới nhất được vá. Các tag cũ giữ nguyên để bảo
đảm tính tái lập của kết quả đã công bố, và sẽ không được cập nhật.
