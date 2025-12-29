# FastAPI Authentication Patterns Guide

**Use this guide when:** Implementing JWT authentication, OAuth2 flows, or securing API endpoints with token-based auth.

## Overall Pattern

```
OAuth2 + JWT Flow
├── Login: POST /token with username/password
├── Hash: Verify password with Argon2 (pwdlib)
├── Token: Generate JWT with expiration (HS256)
├── Storage: Client stores token, sends in Authorization header
├── Validation: Dependency extracts & validates token
└── User: Inject current user into protected endpoints
```

FastAPI provides OAuth2PasswordBearer for standards-compliant authentication. Use Argon2 for password hashing (2025 best practice), JWT for stateless tokens.

---

## Step 1: Install Dependencies and Configure Secrets

```bash
pip install pyjwt
pip install "pwdlib[argon2]"  # Argon2 for password hashing
```

```python
# config.py or settings.py
import os
from datetime import timedelta

# Generate with: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR-SECRET-KEY-HERE")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Optional: Refresh token settings
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

**Rules:**
- Generate SECRET_KEY with `openssl rand -hex 32` (64 chars)
- NEVER commit SECRET_KEY to version control (use .env)
- Use HS256 algorithm for symmetric JWT signing
- Set reasonable expiration (30 min for access, 7 days for refresh)
- Store config in environment variables, not hardcoded

---

## Step 2: Setup Password Hashing with Argon2

```python
from pwdlib import PasswordHash
from pydantic import BaseModel

# Initialize password hasher (Argon2 recommended for 2025)
password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password with Argon2"""
    return password_hash.hash(password)

# Pydantic models
class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool = False

class UserInDB(User):
    hashed_password: str  # NEVER expose this in responses
```

**Rules:**
- Use `PasswordHash.recommended()` for Argon2 (GPU-resistant)
- NEVER store plaintext passwords
- Hash passwords on user creation: `get_password_hash(plain_password)`
- Verify on login: `verify_password(plain, hashed)`
- Keep `UserInDB` separate from response models to prevent password leaks

---

## Step 3: Create JWT Token Functions

```python
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate JWT token with expiration"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise ValueError("Token missing subject")
        return TokenData(username=username)
    except InvalidTokenError:
        raise ValueError("Invalid token")
```

**Rules:**
- Always set expiration (`exp` claim) to prevent token reuse
- Use UTC timezone for consistency (`datetime.now(timezone.utc)`)
- Store user identifier in `sub` claim (e.g., `username:johndoe` or user ID)
- Handle `InvalidTokenError` for expired/malformed tokens
- Return generic errors to prevent username enumeration

---

## Step 4: Implement Authentication Dependencies

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# OAuth2 scheme points to token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Extract and validate user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    # Fetch user from database
    user = await get_user_from_db(username=token_data.username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure user is not disabled (chainable dependency)"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Optional: Role-based dependency
async def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
```

**Rules:**
- `oauth2_scheme` extracts token from `Authorization: Bearer <token>` header
- Chain dependencies for validation layers (token → user → active → role)
- Return 401 for auth failures, 403 for authorization failures
- Use generic error messages to prevent user enumeration
- FastAPI caches dependencies per request (same user object reused)

---

## Step 5: Create Login Endpoint and Protect Routes

```python
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

@app.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """OAuth2-compliant login endpoint"""
    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

# Protected endpoint
@app.get("/users/me", response_model=User)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Get current user info (requires valid token)"""
    return current_user

# Admin-only endpoint
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Annotated[User, Depends(require_admin)]
):
    """Delete user (admin only)"""
    await delete_user_from_db(user_id)
    return {"message": "User deleted"}

async def authenticate_user(username: str, password: str) -> User | None:
    """Verify credentials and return user"""
    user = await get_user_from_db(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
```

**Rules:**
- Use `OAuth2PasswordRequestForm` for standards-compliant login
- Login returns `access_token` and `token_type: "bearer"`
- Protected routes inject `User` via `Depends(get_current_active_user)`
- Return generic errors on failed login (prevent username enumeration)
- Chain dependencies for role-based access control (RBAC)

---

## Quick Checklist

- [ ] SECRET_KEY generated with `openssl rand -hex 32` and stored in env
- [ ] Installed `pyjwt` and `pwdlib[argon2]`
- [ ] Password hashing uses `PasswordHash.recommended()` (Argon2)
- [ ] JWT tokens include `exp` claim with reasonable expiration
- [ ] `oauth2_scheme` configured with correct `tokenUrl`
- [ ] Dependencies chain: token → user → active → role
- [ ] Login endpoint uses `OAuth2PasswordRequestForm`
- [ ] Protected routes use `Depends(get_current_active_user)`
- [ ] Generic error messages to prevent user enumeration
- [ ] Separate `User` and `UserInDB` models to prevent password leaks
