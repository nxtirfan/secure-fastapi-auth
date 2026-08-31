# Secure FastAPI Auth

A secure FastAPI backend that handles user authentication through Supabase Auth — sign up, log in, log out — verifies JSON Web Tokens (JWTs), and protects endpoints behind a reusable bearer-token guard.

## How it works

1. **Sign Up / Log In**: The client sends credentials (`email` and `password`) to `/auth/signup` or `/auth/login`. Supabase hashes passwords, manages accounts, and returns a signed JWT access token.
2. **Protected Requests**: The client calls protected routes with the header `Authorization: Bearer <token>`.
3. **Verification Guard**: A reusable FastAPI dependency extracts the bearer token, verifies it with Supabase (`supabase.auth.get_user(token)`), and injects the user metadata into the route handler only if valid.

No password or cryptography is handled locally — all security is delegated to Supabase Auth.

## Setup & Running

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a free Supabase project at [supabase.com](https://supabase.com).
3. In your Supabase Dashboard, go to **Authentication → Providers → Email** and turn **"Confirm email" OFF** (so new signups can log in immediately).
4. Copy `.env.example` to `.env` and fill in your Project URL and anon/publishable key from **Project Settings → API**:
   ```env
   SUPABASE_URL=https://<your-project-ref>.supabase.co
   SUPABASE_KEY=<your-anon-key>
   PORT=8000
   ```
5. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
6. Open interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Reference

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | `/auth/signup` | No | Create a new user account |
| POST | `/auth/login` | No | Authenticate and return access + refresh tokens |
| POST | `/auth/logout` | Bearer Token | Revoke the session |
| GET | `/public/info` | No | Open public lobby |
| GET | `/protected/profile` | Bearer Token | Read caller's user metadata (`id`, `email`, `created_at`) |
| GET | `/protected/dashboard` | Bearer Token | Second protected route sharing the exact same guard |

## Swagger UI & Bearer Auth

![Swagger UI with Bearer Auth](docs/swagger.png)

Click **Authorize** in Swagger UI, paste your JWT access token from `/auth/login`, and test any protected endpoint directly from the browser.

## Tech Stack

- **Framework**: FastAPI (Python 3.14)
- **Identity Provider**: Supabase Auth (`supabase-py`)
- **Server**: Uvicorn
- **Environment**: `python-dotenv`
