# FastAPI Project Structure Guide

**Use this guide when:** Starting a new FastAPI project or refactoring an existing one for better maintainability and scalability.

## Overall Pattern

```
Domain-Based Structure (Netflix Dispatch-inspired)
src/
├── auth/              # Authentication domain
│   ├── router.py      # Endpoints
│   ├── schemas.py     # Pydantic models
│   ├── models.py      # SQLAlchemy models
│   ├── service.py     # Business logic
│   ├── dependencies.py # Reusable dependencies
│   ├── exceptions.py  # Domain-specific exceptions
│   └── constants.py   # Domain constants
├── posts/             # Posts domain (same structure)
├── users/             # Users domain (same structure)
├── config.py          # App-wide settings
├── database.py        # Database engine/session
└── main.py            # App entry point
```

Organize by **domain/feature** (not file type). Each domain is self-contained with consistent internal structure.

---

## Step 1: Setup Base Project Structure

```bash
# Create domain-based structure
mkdir -p src/{auth,posts,users}
touch src/{__init__.py,main.py,config.py,database.py}

# Each domain has consistent files
for domain in auth posts users; do
    touch src/$domain/{__init__.py,router.py,schemas.py,models.py,service.py,dependencies.py}
done
```

```python
# src/main.py - Application entry point
from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.posts.router import router as posts_router
from src.users.router import router as users_router

app = FastAPI(title="My API", version="1.0.0")

# Register domain routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(users_router, prefix="/users", tags=["users"])
```

**Rules:**
- `src/` is the highest level containing all domains
- Each domain is a Python package with `__init__.py`
- Consistent file naming across domains (router, schemas, models, service)
- `main.py` imports and registers all routers
- Use domain prefixes in router registration

---

## Step 2: Organize Routes with APIRouter

```python
# src/posts/router.py - Domain-specific routing
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.posts.schemas import Post, PostCreate
from src.posts.service import PostService

router = APIRouter()  # Create domain router

@router.get("/", response_model=list[Post])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """THIN route - delegates to service layer"""
    service = PostService(db)
    return await service.get_posts(skip=skip, limit=limit)

@router.post("/", response_model=Post, status_code=201)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db)
):
    """THIN route - only handles HTTP concerns"""
    service = PostService(db)
    return await service.create_post(post)
```

**Rules:**
- Each domain has one `APIRouter()` instance
- Routes are THIN - delegate business logic to services
- Routes handle: request/response, validation, status codes
- Use dependency injection for database sessions
- Group related endpoints in same router

---

## Step 3: Separate Schemas (Pydantic) and Models (SQLAlchemy)

```python
# src/posts/schemas.py - Request/Response validation
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    """Request schema for creating posts"""
    pass

class Post(PostBase):
    """Response schema with database fields"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2

# src/posts/models.py - Database tables
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from datetime import datetime

class PostModel(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    content: Mapped[str]
    created_at: Mapped[datetime]
```

**Rules:**
- `schemas.py`: Pydantic models for request/response validation
- `models.py`: SQLAlchemy models for database tables
- Inherit schemas: Base → Create → Update → Response
- Use `from_attributes=True` for ORM compatibility (Pydantic v2)
- Name database models with `Model` suffix to avoid conflicts

---

## Step 4: Implement Service Layer for Business Logic

```python
# src/posts/service.py - Business logic and database operations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.posts.models import PostModel
from src.posts.schemas import PostCreate

class PostService:
    """Encapsulates posts business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_posts(self, skip: int = 0, limit: int = 10) -> list[PostModel]:
        """Fetch paginated posts"""
        result = await self.db.execute(
            select(PostModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create_post(self, post: PostCreate) -> PostModel:
        """Create new post with validation"""
        db_post = PostModel(**post.dict())
        self.db.add(db_post)
        await self.db.commit()
        await self.db.refresh(db_post)
        return db_post

    async def get_post_with_author(self, post_id: int):
        """Complex business logic - SQL-first approach"""
        query = """
            SELECT json_build_object(
                'post', p.*,
                'author', u.*
            ) FROM post p
            JOIN user u ON p.user_id = u.id
            WHERE p.id = :post_id
        """
        result = await self.db.execute(query, {"post_id": post_id})
        return result.scalar_one_or_none()
```

**Rules:**
- Services contain ALL business logic and database queries
- Routes call services, services call database
- Services are testable independently from HTTP layer
- Prefer SQL operations (joins, aggregations) over Python loops
- One service class per domain

---

## Step 5: Use Dependencies for Reusable Logic

```python
# src/posts/dependencies.py - Domain-specific dependencies
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.posts.service import PostService
from src.posts.models import PostModel

async def get_post_or_404(
    post_id: int,
    db: AsyncSession = Depends(get_db)
) -> PostModel:
    """Reusable dependency to fetch post or raise 404"""
    service = PostService(db)
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Use in routes
from src.posts.dependencies import get_post_or_404

@router.get("/{post_id}", response_model=Post)
async def get_post(post: PostModel = Depends(get_post_or_404)):
    """Dependency injects validated post"""
    return post

@router.put("/{post_id}", response_model=Post)
async def update_post(
    post_update: PostUpdate,
    post: PostModel = Depends(get_post_or_404),  # Reused!
    db: AsyncSession = Depends(get_db)
):
    """Same dependency ensures post exists"""
    service = PostService(db)
    return await service.update_post(post, post_update)
```

**Rules:**
- Dependencies validate and inject complex objects (not just primitives)
- Dependencies are cached per request (no redundant DB calls)
- Use for: authentication, resource validation, permission checks
- Keep dependencies async for performance
- Chain dependencies for layered validation

---

## Step 6: Handle Cross-Domain Imports Explicitly

```python
# ❌ AVOID - Ambiguous relative imports
from ..auth import constants

# ✅ CORRECT - Explicit absolute imports
from src.auth import constants as auth_constants
from src.posts import constants as post_constants

# In routers that need auth
from src.auth.dependencies import get_current_active_user

@router.post("/", response_model=Post)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_active_user),  # Cross-domain dependency
    db: AsyncSession = Depends(get_db)
):
    service = PostService(db)
    return await service.create_post(post, user=current_user)
```

**Rules:**
- Always use absolute imports from `src.domain.module`
- Alias when importing same-named modules from different domains
- Dependencies can be shared across domains
- Avoid circular imports (domain A → domain B → domain A)

---

## Quick Checklist

- [ ] Project uses `src/` as root with domain-based folders
- [ ] Each domain has: router, schemas, models, service, dependencies
- [ ] `main.py` registers all routers with domain prefixes
- [ ] Routes are thin and delegate to service layer
- [ ] `schemas.py` contains Pydantic models (validation)
- [ ] `models.py` contains SQLAlchemy models (database)
- [ ] Business logic lives in `service.py`, not routes
- [ ] Dependencies used for validation and resource injection
- [ ] Cross-domain imports use absolute paths (`from src.domain`)
- [ ] Consistent naming: singular table names, `_at` for datetime
