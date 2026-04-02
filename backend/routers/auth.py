"""Authentication router — JWT login & registration with bcrypt."""

from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import Optional
import hashlib
import secrets
import time
import uuid
import jwt  # type: ignore
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_SECONDS  # type: ignore
from middleware.sanitizer import sanitize_string  # type: ignore

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = JWT_SECRET
ALGORITHM = JWT_ALGORITHM
TOKEN_EXPIRE = JWT_EXPIRE_SECONDS

security = HTTPBearer()
_executor = ThreadPoolExecutor(max_workers=2)

# In-memory user store (fallback when Supabase is unavailable)
_users: dict = {}


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _hash_password(password: str) -> str:
    """Hash password using bcrypt. Falls back to SHA256 if bcrypt is unavailable."""
    try:
        import bcrypt  # type: ignore
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash. Supports both bcrypt and SHA256."""
    try:
        import bcrypt  # type: ignore
        if password_hash.startswith("$2"):  # bcrypt hash
            return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ImportError:
        pass
    # Fallback: SHA256 comparison
    return hashlib.sha256(password.encode()).hexdigest() == password_hash


def _create_token(user_id: str, email: str, name: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "exp": time.time() + TOKEN_EXPIRE,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to verify JWT tokens."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")


def _supabase_register(email: str, name: str, password_hash: str, user_id: str):
    """Run Supabase registration in a thread with implicit timeout."""
    from services.supabase_client import get_supabase  # type: ignore
    sb = get_supabase()
    existing = sb.table("profiles").select("id").eq("email", email).execute()
    if existing.data:
        return {"error": "exists"}
    sb.table("profiles").insert({
        "id": user_id,
        "email": email,
        "name": name,
        "password_hash": password_hash,
    }).execute()
    return {"ok": True}


def _supabase_login(email: str, password_hash: str):
    """Run Supabase login lookup in a thread with implicit timeout."""
    from services.supabase_client import get_supabase  # type: ignore
    sb = get_supabase()
    result = sb.table("profiles").select("*").eq("email", email).execute()
    return result.data


@router.post("/register")
async def register(req: RegisterRequest):
    """Register a new user."""
    email = sanitize_string(req.email.lower().strip())
    name = sanitize_string(req.name)
    user_id = str(uuid.uuid4())
    password_hash = _hash_password(req.password)

    # Try Supabase with a 8-second timeout
    try:
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, _supabase_register, email, req.name, password_hash, user_id),
            timeout=8.0,
        )
        if result.get("error") == "exists":
            raise HTTPException(status_code=400, detail="Email already registered")

        token = _create_token(user_id, email, req.name)
        return {"token": token, "user": {"id": user_id, "name": req.name, "email": email}}

    except HTTPException:
        raise
    except (asyncio.TimeoutError, Exception) as e:
        # Fallback to in-memory if Supabase is down/slow
        print(f"[AUTH] Supabase unavailable ({type(e).__name__}), using in-memory fallback")
        if email in _users:
            raise HTTPException(status_code=400, detail="Email already registered")

        _users[email] = {
            "id": user_id,
            "name": req.name,
            "email": email,
            "password_hash": password_hash,
        }
        token = _create_token(user_id, email, req.name)
        return {"token": token, "user": {"id": user_id, "name": req.name, "email": email}}


@router.post("/login")
async def login(req: LoginRequest):
    """Authenticate and return JWT token."""
    email = req.email.lower().strip()
    password_hash = _hash_password(req.password)
    print(f"[AUTH] Login attempt for: {email}")

    # Try Supabase with a 8-second timeout
    try:
        loop = asyncio.get_event_loop()
        data = await asyncio.wait_for(
            loop.run_in_executor(_executor, _supabase_login, email, password_hash),
            timeout=8.0,
        )

        print(f"[AUTH] Supabase returned {len(data) if data else 0} row(s) for {email}")

        if data:
            user = data[0]
            if not _verify_password(req.password, user.get("password_hash", "")):
                print(f"[AUTH] Password mismatch for {email}")
                raise HTTPException(status_code=401, detail="Invalid email or password")
            print(f"[AUTH] Login successful for {email}")
            token = _create_token(user["id"], email, user["name"])
            return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": email}}
        else:
            # User not found in Supabase — check in-memory too
            print(f"[AUTH] User {email} not found in Supabase, checking in-memory")
            mem_user = _users.get(email)
            # For in-memory users, use direct verification
            if mem_user and _verify_password(req.password, mem_user["password_hash"]):
                token = _create_token(mem_user["id"], email, mem_user["name"])
                return {"token": token, "user": {"id": mem_user["id"], "name": mem_user["name"], "email": email}}
            raise HTTPException(status_code=401, detail="Invalid email or password")

    except HTTPException:
        raise
    except (asyncio.TimeoutError, Exception) as e:
        # Fallback to in-memory
        print(f"[AUTH] Supabase unavailable ({type(e).__name__}), using in-memory fallback")
        user = _users.get(email)
        if not user or not _verify_password(req.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = _create_token(user["id"], email, user["name"])
        return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": email}}


@router.get("/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current authenticated user info."""
    return {
        "user_id": payload["user_id"],
        "email": payload["email"],
        "name": payload["name"],
    }
