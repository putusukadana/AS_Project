# Issue: Perbaikan JWT Authentication

## Status: ✅ SELESAI (2026-06-21)

| # | Item | Status |
|---|------|--------|
| 1 | `get_current_user()` di `auth.py` | ✅ |
| 2 | `user_id` di payload JWT (`user_service.py`) | ✅ |
| 3 | `GET /me` di `user_routes.py` | ✅ |
| 4 | `Depends(get_current_user)` di `crawl_routes.py` | ✅ |
| 5 | `Depends(get_current_user)` di `pipeline_routes.py` | ✅ |
| 6 | `Depends(get_current_user)` di `analysis_routes.py` | ✅ |
| 7 | `Depends(get_current_user)` di `upload_routes.py` | ✅ |
| 8 | `Depends(get_current_user)` di `settings_routes.py` | ✅ |

## Masalah

Backend tidak pernah memverifikasi JWT token. Semua endpoint (`/crawl`, `/pipeline`, `/analysis`, `/upload`, `/settings`) dapat diakses tanpa login.

### Flow Setelah Fix

```
[Login] → POST /api/v1/users/login → JWT dibuat → disimpan di localStorage
         ↓
[API Call] → Axios interceptor → Header: Bearer {token}
         ↓
[Backend]  → ✅ verifikasi token via get_current_user()
              ↓ valid
         ✅ lanjut ke handler
              ↓ invalid / expired / no token
         ❌ HTTP 401 Unauthorized
```

### Daftar Issue

| # | Issue | Severity |
|---|-------|----------|
| 1 | Backend tidak pernah verifikasi JWT | 🔴 Critical |
| 2 | Tidak ada refresh token (expire 30 menit) | 🟡 Medium |
| 3 | Tidak ada endpoint `/users/me` | 🟡 Medium |
| 4 | SECRET_KEY fallback hardcoded di source code | 🟡 Medium |
| 5 | Payload JWT minim (hanya `sub: email`) | 🟢 Low |

---

## Implementasi Selesai

### 1. `backend/auth.py` — Ditambahkan `get_current_user` dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from database import db

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = await db["users"].find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### 2. Ditambahkan `user_id` di payload JWT (`user_service.py`)

Payload berubah dari `{"sub": email}` menjadi `{"sub": email, "user_id": "..."}`.

### 3. Semua route — Ditambahkan `Depends(get_current_user)`

| File | Endpoint | Perubahan |
|------|----------|-----------|
| `backend/routes/crawl_routes.py` | `POST /start`, `GET /quota` | + parameter `user = Depends(get_current_user)` |
| `backend/routes/pipeline_routes.py` | Setiap step | + parameter `user = Depends(get_current_user)` |
| `backend/routes/analysis_routes.py` | `POST /sentiment`, `POST /keywords` | + parameter `user = Depends(get_current_user)` |
| `backend/routes/upload_routes.py` | `POST /file` | + parameter `user = Depends(get_current_user)` |
| `backend/routes/settings_routes.py` | `GET/PUT /rapidapi-key` | + parameter `user = Depends(get_current_user)` |

Semua endpoint sekarang memiliki parameter `user = Depends(get_current_user)`.

### 4. `backend/routes/user_routes.py` — Ditambahkan `GET /me`

```python
@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return APIResponse(
        message="User fetched successfully",
        data=format_user_response(user)
    )
```

### 5. File yang diubah (✅ semua selesai)

| File | Perubahan |
|------|-----------|
| `backend/auth.py` | Tambah import + `get_current_user()` + `security` + `user_id` di payload |
| `backend/services/user_service.py` | Tambah `user_id` di argumen `create_access_token()` |
| `backend/routes/crawl_routes.py` | Tambah `Depends(get_current_user)` di setiap endpoint |
| `backend/routes/pipeline_routes.py` | Sama |
| `backend/routes/analysis_routes.py` | Sama |
| `backend/routes/upload_routes.py` | Sama |
| `backend/routes/settings_routes.py` | Sama |
| `backend/routes/user_routes.py` | Tambah `GET /me` |

### Testing

1. Panggil endpoint **tanpa header Authorization** → harus return **401**
2. Panggil dengan **token invalid/expired** → harus return **401**
3. Panggil dengan **token valid** → sukses ✅
4. `GET /api/v1/users/me` → return data user ✅

### Catatan

- Token tetap expire 30 menit. Refresh token bisa ditambahkan di iterasi berikutnya.
- SECRET_KEY tetap di `.env`. Fallback hardcode akan tetap ada untuk development, tapi endpoint tetap terproteksi.
- `get_current_user` tidak dipakai untuk authorization logic (siapa boleh akses apa) — hanya untuk **authentication** (siapa yang mengakses).
