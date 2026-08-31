# Improved Prompt (V2 — Rematch)

```text
Build a secure FastAPI REST API integrated with Supabase Auth.

Endpoints required:
1. POST /auth/signup (201 Created)
2. POST /auth/login (200 OK returning access_token and refresh_token)
3. POST /auth/logout (204 No Content)
4. GET /public/info (200 OK)
5. GET /protected/profile (200 OK returning user id, email, created_at)
6. GET /protected/dashboard (200 OK)

Security & Implementation Specifications:
- Use `HTTPBearer(auto_error=False)` dependency scheme so Swagger UI (/docs) renders the Authorize padlock icon.
- Token extraction must defensively parse "Bearer <token>" and handle missing, empty, or non-Bearer headers with explicit 401 Unauthorized (`{"error": "Access token required"}`) instead of causing 500 IndexErrors.
- Verify JWT tokens via `supabase.auth.get_user(token)`. Handle invalid/expired tokens with 401 (`{"error": "Invalid or expired token"}`).
- Add custom exception handlers for HTTPException and RequestValidationError to guarantee all error responses follow `{"error": "<message>"}` structure.
- Input validation: Pydantic model with optional fields; manual check returning 400 (`{"error": "Fields 'email' and 'password' are required"}`).
- Stateless logout: Revoke token session via `supabase.auth.admin.sign_out(token)`.
```

## Summary of Prompt Improvement (1 Sentence)
Prompt V2 explicitly defines the `HTTPBearer` security scheme for Swagger UI, demands defensive header parsing to eliminate 500 `IndexError` vulnerabilities, and enforces strict `{"error": "..."}` JSON response schemas across all endpoints.
