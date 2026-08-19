from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

EVIL_ORIGIN = "https://evil-attacker.xyz"
GOOD_ORIGIN = "https://internal.megamart.com"


# ---------- Test phân quyền (RBAC Middleware) ----------

def test_staff_bi_chan_truy_cap_system_settings():
    res = client.get("/api/v1/system/settings", headers={"X-User-Role": "STAFF"})
    assert res.status_code == 403
    assert res.json() == {"error": "Permission Denied"}


def test_admin_duoc_phep_truy_cap_system_settings():
    res = client.get("/api/v1/system/settings", headers={"X-User-Role": "ADMIN"})
    assert res.status_code == 200


def test_hr_bi_chan_truy_cap_system_settings():
    res = client.get("/api/v1/system/settings", headers={"X-User-Role": "HR"})
    assert res.status_code == 403


def test_hr_duoc_phep_truy_cap_salary_modify():
    res = client.get("/api/v1/salary/modify", headers={"X-User-Role": "HR"})
    assert res.status_code == 200


def test_staff_bi_chan_truy_cap_salary_modify():
    res = client.get("/api/v1/salary/modify", headers={"X-User-Role": "STAFF"})
    assert res.status_code == 403


def test_ba_vai_tro_deu_duoc_phep_truy_cap_profile():
    for role in ("ADMIN", "HR", "STAFF"):
        res = client.get("/api/v1/profile", headers={"X-User-Role": role})
        assert res.status_code == 200


def test_khong_gui_header_role_bi_chan():
    res = client.get("/api/v1/system/settings")
    assert res.status_code == 403


def test_role_khong_hop_le_bi_chan():
    res = client.get("/api/v1/profile", headers={"X-User-Role": "HACKER"})
    assert res.status_code == 403


# ---------- Test CORS ----------

def test_preflight_tu_domain_hop_le_duoc_chap_nhan():
    res = client.options(
        "/api/v1/salary/modify",
        headers={
            "Origin": GOOD_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-User-Role",
        },
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == GOOD_ORIGIN


def test_preflight_tu_domain_gia_mao_bi_tu_choi():
    res = client.options(
        "/api/v1/salary/modify",
        headers={
            "Origin": EVIL_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-User-Role",
        },
    )
    # Starlette CORSMiddleware trả 400 khi Origin không nằm trong allow_origins
    assert res.status_code == 400
    assert "access-control-allow-origin" not in res.headers


def test_request_thuc_tu_domain_gia_mao_khong_co_header_cors():
    res = client.get(
        "/api/v1/profile",
        headers={"Origin": EVIL_ORIGIN, "X-User-Role": "ADMIN"},
    )
    # Server vẫn xử lý request (CORS là cơ chế phía trình duyệt), nhưng
    # KHÔNG trả về Access-Control-Allow-Origin cho origin lạ nên trình
    # duyệt của nạn nhân sẽ chặn JS đọc response.
    assert "access-control-allow-origin" not in res.headers


def test_request_thuc_tu_domain_hop_le_co_header_cors():
    res = client.get(
        "/api/v1/profile",
        headers={"Origin": GOOD_ORIGIN, "X-User-Role": "ADMIN"},
    )
    assert res.headers.get("access-control-allow-origin") == GOOD_ORIGIN


def test_method_khong_cho_phep_bi_tu_choi_o_preflight():
    res = client.options(
        "/api/v1/salary/modify",
        headers={
            "Origin": GOOD_ORIGIN,
            "Access-Control-Request-Method": "DELETE",
        },
    )
    assert res.status_code == 400
