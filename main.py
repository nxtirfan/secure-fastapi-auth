import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    health = httpx.get(
        f"{SUPABASE_URL}/auth/v1/health", headers={"apikey": SUPABASE_KEY}
    )
    if health.status_code == 200:
        print("Server running and connected to Supabase")
    else:
        print(f"Server running, but Supabase health check returned {health.status_code}")
    yield


app = FastAPI(
    title="Secure FastAPI Auth",
    description="A secure API that handles user authentication (sign up, log in, log out) "
    "through Supabase Auth, verifies JSON Web Tokens, and protects routes behind "
    "a bearer-token guard.",
    version="1.0",
    lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


class Credentials(BaseModel):
    email: str | None = None
    password: str | None = None


@app.get("/", tags=["General"])
def read_root():
    """Describe this API: its name, version, and the doors it offers."""
    return {
        "name": "Secure FastAPI Auth",
        "version": "1.0",
        "endpoints": [
            "/auth/signup",
            "/auth/login",
            "/auth/logout",
            "/public/info",
            "/protected/profile",
            "/protected/dashboard",
        ],
    }


@app.post("/auth/signup", status_code=201, tags=["Auth"])
def signup(credentials: Credentials):
    """Create a new user account in Supabase Auth."""
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Fields 'email' and 'password' are required")
    try:
        response = supabase.auth.sign_up(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Signup failed: {exc}") from exc
    user = response.user
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "message": "User created. You can now log in.",
    }


@app.post("/auth/login", tags=["Auth"])
def login(credentials: Credentials):
    """Authenticate a user and return the Supabase access and refresh tokens."""
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Fields 'email' and 'password' are required")
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid login credentials") from exc
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "token_type": "bearer",
        "user": {"id": response.user.id, "email": response.user.email},
    }


bearer_scheme = HTTPBearer(auto_error=False)


def parse_bearer_token(authorization: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    """Pull the bearer token from the Authorization header using FastAPI's HTTPBearer scheme."""
    if authorization is None or authorization.scheme.lower() != "bearer" or not authorization.credentials:
        raise HTTPException(status_code=401, detail="Access token required")
    return authorization.credentials


def require_user(token: str = Depends(parse_bearer_token)) -> dict:
    """Reusable guard: verify the token with Supabase and return safe user metadata."""
    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = response.user
    if user is None or getattr(user, "id", None) is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@app.get("/public/info", tags=["Public"])
def public_info():
    """Open lobby: no authentication needed."""
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", tags=["Protected"])
def protected_profile(user: dict = Depends(require_user)):
    """Read private profile data using the reusable guard."""
    return user


@app.get("/protected/dashboard", tags=["Protected"])
def protected_dashboard(user: dict = Depends(require_user)):
    """A second locked door behind the same guard — zero new auth code."""
    return {
        "message": f"Welcome to your dashboard, {user['email']}",
        "user_id": user["id"],
        "notes_count": 0,
    }


@app.post("/auth/logout", status_code=204, tags=["Auth"])
def logout(token: str = Depends(parse_bearer_token), user: dict = Depends(require_user)):
    """End the session by revoking tokens via Supabase admin sign_out."""
    try:
        supabase.auth.admin.sign_out(token)
    except Exception:
        pass
    return None
