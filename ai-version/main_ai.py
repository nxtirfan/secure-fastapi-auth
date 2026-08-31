import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="AI Generated Auth API")


class UserAuth(BaseModel):
    email: str
    password: str


def get_current_user(authorization: str = Header(...)):
    # AI Flaw 1: Naive split - if header is just 'Bearer' or lacks space, split()[1] raises IndexError -> 500 Server Error
    token = authorization.split(" ")[1]
    try:
        user_response = supabase.auth.get_user(token)
        # AI Flaw 2: Assumes user_response is non-null without checking user_response.user
        return user_response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/auth/signup", status_code=201)
def signup(auth: UserAuth):
    try:
        res = supabase.auth.sign_up({"email": auth.email, "password": auth.password})
        return res.user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login")
def login(auth: UserAuth):
    try:
        res = supabase.auth.sign_in_with_password({"email": auth.email, "password": auth.password})
        return {
            "access_token": res.session.access_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")


@app.get("/public/info")
def public_info():
    return {"message": "Public information"}


@app.get("/protected/profile")
def profile(user=Depends(get_current_user)):
    return {"user": user}


@app.post("/auth/logout", status_code=204)
def logout(user=Depends(get_current_user)):
    # AI Flaw 3: Calls sign_out() on client without token argument, which depends on local session state
    supabase.auth.sign_out()
    return None
