# Stage 7: AI Rematch Analysis

## Overview
In Stage 7, an AI was prompted to build the same Supabase-authenticated FastAPI application in a quarantined directory (`ai-version/`). The generated implementation (`main_ai.py`) was tested against our Stage 3 and Stage 4 security checkpoints and diffed against our manual implementation (`main.py`).

---

## 1. How did it handle token extraction?
- **AI Implementation**: Used `authorization: str = Header(...)` with naive string splitting: `token = authorization.split(" ")[1]`.
- **Vulnerability**: When sent a malformed header such as `Authorization: Bearer` (missing token) or `Authorization: mytoken` (missing `Bearer ` prefix), Python's `split(" ")` returns a list with length 1. Accessing index `[1]` throws an unhandled `IndexError`, causing the server to return **500 Internal Server Error** instead of **401 Unauthorized**.
- **My Implementation**: Used FastAPI's `HTTPBearer(auto_error=False)` combined with explicit scheme and credential validation (`authorization.scheme.lower() != "bearer"`), safely returning a clean **401 Unauthorized** with `{"error": "Access token required"}`.

---

## 2. What security flaws or issues did it introduce?
1. **Stateless Logout Failure**: The AI implemented `/auth/logout` by calling `supabase.auth.sign_out()` without passing a token or utilizing admin session revocation. In a stateless API, this attempts to sign out whatever session happens to be stored on the global SDK client instance rather than revoking the specific requesting caller's token.
2. **Non-standard Error Schema**: Instead of returning the required `{"error": "<message>"}` structure, the AI relied on FastAPI defaults, returning `{"detail": "<message>"}` or uncaught exception strings.
3. **Missing OpenAPI Security**: The AI omitted `HTTPBearer` scheme integration, leaving Swagger UI (`/docs`) without the Authorize padlock icon.

---

## 3. What did the prompt forget to specify — and what did the AI silently decide?
- **Omitted in Prompt V1**:
  - Exact JSON error structure (`{"error": "..."}`).
  - Requirement for FastAPI's `HTTPBearer` security scheme for Swagger UI authorization.
  - Defensive string parsing requirements for bearer headers.
- **AI Silent Decisions**:
  - The AI assumed `Header(...)` with naive `split()` was sufficient for bearer token parsing.
  - The AI chose default `{"detail": ...}` error responses.
  - The AI assumed single-user client-side state for `sign_out()`.

---

## Prompt Evolution (V1 vs V2)

### Prompt V1 (Initial)
> See `prompt_v1.md`

### Prompt V2 (Rematch)
> See `prompt_v2.md`

**Key Change (1 Sentence)**: Prompt V2 explicitly specifies `HTTPBearer` security scheme integration for Swagger UI, demands defensive header parsing to prevent 500 `IndexError` vulnerabilities, and enforces strict `{"error": "..."}` JSON response schemas across all endpoints.
