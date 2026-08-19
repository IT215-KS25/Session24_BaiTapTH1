# BTTH — Middleware Phân Quyền & CORS cho hệ thống ERP MegaMart

## Cấu trúc
- `main.py` — app FastAPI, `RoleAuthorizationMiddleware` (RBAC tập trung) + cấu hình `CORSMiddleware` nghiêm ngặt
- `requirements.txt` — thư viện cần cài
- `test_main.py` — 13 test case tự động (pytest)
- `TEST_CASES.md` — kịch bản kiểm thử + log request/response thật làm minh chứng

## Vai trò & phân quyền
| Endpoint | ADMIN | HR | STAFF |
|---|---|---|---|
| GET /api/v1/salary/modify | ✅ | ✅ | ❌ |
| GET /api/v1/system/settings | ✅ | ❌ | ❌ |
| GET /api/v1/profile | ✅ | ✅ | ✅ |

Vai trò được đọc từ header `X-User-Role` (giả lập, chưa gắn JWT thật —
đúng phạm vi bài yêu cầu). Middleware so khớp `(method, path)` request với
bảng `ROUTE_PERMISSIONS`; sai/thiếu vai trò → `403 {"error": "Permission Denied"}`.

## CORS
- Không dùng `*`.
- Chỉ cho phép `https://internal.megamart.com`.
- Chỉ cho phép method `GET`, `POST`.
- Chỉ cho phép header `Content-Type`, `X-User-Role`.

`CORSMiddleware` được đăng ký **trước** `RoleAuthorizationMiddleware` để nằm
ngoài cùng pipeline, xử lý preflight `OPTIONS` (kể cả khi bị từ chối) trước
khi request chạm tới middleware phân quyền.

## Chạy thử
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Chạy test
```bash
pytest test_main.py -v
```
