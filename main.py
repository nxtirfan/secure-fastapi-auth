import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
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
        ],
    }
