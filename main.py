from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

ALLOWED_ORIGIN = "https://internal.megamart.com"

# (method, path) -> tập vai trò được phép truy cập
ROUTE_PERMISSIONS = {
    ("GET", "/api/v1/salary/modify"): {"ADMIN", "HR"},
    ("GET", "/api/v1/system/settings"): {"ADMIN"},
    ("GET", "/api/v1/profile"): {"ADMIN", "HR", "STAFF"},
}


class RoleAuthorizationMiddleware(BaseHTTPMiddleware):
    """Middleware phân quyền tập trung: chặn request trước khi vào Controller."""

    async def dispatch(self, request: Request, call_next):
        # OPTIONS preflight do CORSMiddleware xử lý, không kiểm tra role ở đây
        if request.method == "OPTIONS":
            return await call_next(request)

        required_roles = ROUTE_PERMISSIONS.get((request.method, request.url.path))

        if required_roles is not None:
            role = request.headers.get("X-User-Role")
            if role not in required_roles:
                return JSONResponse(status_code=403, content={"error": "Permission Denied"})

        return await call_next(request)


app = FastAPI(title="MegaMart ERP - RBAC Middleware & CORS")

# CORSMiddleware phải được đăng ký trước để nằm ngoài cùng trong pipeline,
# xử lý preflight OPTIONS trước khi request chạm tới middleware phân quyền.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-User-Role"],
)

app.add_middleware(RoleAuthorizationMiddleware)


@app.get("/api/v1/salary/modify")
def modify_salary():
    return {"message": "Truy cap API sua luong thanh cong"}


@app.get("/api/v1/system/settings")
def system_settings():
    return {"message": "Truy cap cau hinh he thong thanh cong"}


@app.get("/api/v1/profile")
def profile():
    return {"message": "Truy cap thong tin ca nhan thanh cong"}
