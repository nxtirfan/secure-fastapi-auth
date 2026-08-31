# Initial Prompt (V1)

```text
Build a FastAPI REST API that uses Supabase Auth for user authentication.

The API should have five endpoints:
- POST /auth/signup (201 Created)
- POST /auth/login (200 OK with JWT access_token)
- POST /auth/logout (204 No Content)
- GET /public/info (200 OK public message)
- GET /protected/profile (200 OK with user profile)

Requirements:
- Use pydantic for request validation (400 Bad Request on missing fields).
- Protect /protected/profile and /auth/logout with a reusable FastAPI dependency/middleware that verifies the Supabase JWT token using `supabase.auth.get_user()`.
- Return 401 Unauthorized if the token is missing, malformed, or invalid.
- Configure Swagger UI (/docs) with bearer token authorization.
```
