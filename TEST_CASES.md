# Kịch bản kiểm thử (Test Cases) — RBAC Middleware & CORS

Toàn bộ kịch bản dưới đây được tự động hóa trong `test_main.py` (13 test case,
chạy bằng `pytest`, **13/13 PASSED**) và được chạy trực tiếp một lần nữa bên
dưới để ghi lại log request/response thật làm minh chứng.

## A. Test phân quyền (RBAC Middleware)

### A1. STAFF gọi `/api/v1/system/settings` → phải bị chặn 403

Request:
```
GET /api/v1/system/settings
X-User-Role: STAFF
```

Kết quả thực tế:
```
Status: 403
Body: {"error": "Permission Denied"}
```
✅ Đúng yêu cầu đề bài.

### A2. ADMIN gọi `/api/v1/system/settings` → phải được phép 200

Request:
```
GET /api/v1/system/settings
X-User-Role: ADMIN
```

Kết quả thực tế:
```
Status: 200
Body: {"message": "Truy cap cau hinh he thong thanh cong"}
```
✅ Đúng yêu cầu đề bài.

### A3. Các trường hợp còn lại (được tự động test trong `test_main.py`)

| # | Role | Endpoint | Kỳ vọng | Kết quả |
|---|---|---|---|---|
| 1 | STAFF | GET /api/v1/system/settings | 403 | PASSED |
| 2 | ADMIN | GET /api/v1/system/settings | 200 | PASSED |
| 3 | HR | GET /api/v1/system/settings | 403 | PASSED |
| 4 | HR | GET /api/v1/salary/modify | 200 | PASSED |
| 5 | STAFF | GET /api/v1/salary/modify | 403 | PASSED |
| 6 | ADMIN/HR/STAFF | GET /api/v1/profile | 200 (cả 3) | PASSED |
| 7 | (không gửi header role) | GET /api/v1/system/settings | 403 | PASSED |
| 8 | HACKER (role không tồn tại) | GET /api/v1/profile | 403 | PASSED |

## B. Test CORS

### B1. Preflight OPTIONS từ domain hợp lệ `https://internal.megamart.com`

Request:
```
OPTIONS /api/v1/salary/modify
Origin: https://internal.megamart.com
Access-Control-Request-Method: GET
Access-Control-Request-Headers: X-User-Role
```

Kết quả thực tế:
```
Status: 200
Access-Control-Allow-Origin: https://internal.megamart.com
```
✅ Frontend chính thức của công ty hoạt động bình thường.

### B2. Preflight OPTIONS từ domain giả mạo `https://evil-attacker.xyz`

Request:
```
OPTIONS /api/v1/salary/modify
Origin: https://evil-attacker.xyz
Access-Control-Request-Method: GET
Access-Control-Request-Headers: X-User-Role
```

Kết quả thực tế:
```
Status: 400
Access-Control-Allow-Origin: (không có)
Body: Disallowed CORS origin
```
✅ Trình duyệt của nạn nhân sẽ nhận diện đây là preflight bị từ chối và
**không gửi tiếp request thật**, chặn đứng kịch bản tấn công CSRF/đánh cắp
dữ liệu mô tả trong đề bài.

### B3. Request GET thật từ domain giả mạo (không phải preflight)

Với các request "đơn giản" (simple request — GET không có custom header cần
preflight), CORS là cơ chế **phía trình duyệt**, server vẫn xử lý và trả dữ
liệu, nhưng do response **không có** header `Access-Control-Allow-Origin`
khớp với origin của kẻ tấn công, trình duyệt sẽ chặn JavaScript trên trang
`evil-attacker.xyz` đọc được nội dung response (`fetch()`/`XMLHttpRequest`
báo lỗi CORS).

Kết quả thực tế: response cho request có `Origin: https://evil-attacker.xyz`
không chứa header `access-control-allow-origin`, trong khi request có
`Origin: https://internal.megamart.com` có header này với đúng giá trị domain
công ty.

### B4. Method không được phép (DELETE) bị từ chối ngay ở preflight

```
OPTIONS /api/v1/salary/modify
Origin: https://internal.megamart.com
Access-Control-Request-Method: DELETE
```
Kết quả thực tế: `Status: 400` — vì `allow_methods` chỉ khai báo
`["GET", "POST"]`, không có `DELETE`.

## Cách tự chạy lại toàn bộ kịch bản

```bash
pip install -r requirements.txt
pytest test_main.py -v
```
