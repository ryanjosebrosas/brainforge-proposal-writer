# FastAPI Database Patterns Guide

**Use this guide when:** Setting up databases with async SQLAlchemy 2.0, managing sessions, or configuring migrations.

## Overall Pattern

```
Database Layer Architecture
├── Engine: Single async engine per app (postgresql+asyncpg://)
├── SessionMaker: Factory with expire_on_commit=False
├── Dependency: Yields session per request, auto-cleanup
├── Models: SQLAlchemy ORM with naming conventions
└── Migrations: Alembic with human-readable filenames
```

Use async everywhere. One engine, one sessionmaker, dependency injection for sessions. Sessions are request-scoped and automatically closed.

---

## Step 1: Configure Async Engine with Naming Conventions

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import MetaData

# Database naming conventions for consistent index names
NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

# Create async engine
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set False in production
    future=True,  # SQLAlchemy 2.0 mode
    pool_pre_ping=True,  # Verify connections before use
)
```

**Rules:**
- Use `postgresql+asyncpg://` driver for async Postgres (or `sqlite+aiosqlite://` for SQLite)
- Define naming conventions at metadata level for Alembic compatibility
- Use `pool_pre_ping=True` to handle stale connections
- Set `echo=True` only in development for SQL logging
- Create ONE engine per application lifetime

---

## Step 2: Create Async Session Factory

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from collections.abc import AsyncIterator

# Create session factory (NOT per-request)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL: Prevents implicit I/O after commit
    autoflush=False,  # Explicit control over flushes
)

# Dependency for FastAPI
async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Auto-rollback on error
            raise
        finally:
            await session.close()
```

**Rules:**
- Create sessionmaker ONCE at startup (not per request)
- Set `expire_on_commit=False` to avoid lazy-loading errors after commit
- Dependency yields session, handles commit/rollback/close automatically
- One session per request via FastAPI's dependency injection
- Always use async context manager pattern

---

## Step 3: Define Models with Database Conventions

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    metadata = metadata  # Use the metadata with naming conventions

class Post(Base):
    __tablename__ = "post"  # Singular, lowercase, snake_case

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    content: Mapped[str]
    created_at: Mapped[datetime]  # _at suffix for datetime
    published_date: Mapped[date | None]  # _date suffix for date

    # Module-prefixed naming for multi-domain apps
    # user_id, post_id, comment_id, etc.
```

**Rules:**
- Table names: lowercase, snake_case, SINGULAR form (`post` not `posts`)
- Datetime columns: `_at` suffix (e.g., `created_at`, `updated_at`)
- Date columns: `_date` suffix (e.g., `published_date`, `birth_date`)
- Foreign keys: module-prefixed (e.g., `user_id`, `post_id`)
- Use SQLAlchemy 2.0 `Mapped` type annotations

---

## Step 4: Use Sessions in Routes with Dependency Injection

```python
from fastapi import Depends, FastAPI
from sqlalchemy import select

app = FastAPI()

@app.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):
    # All database I/O requires await
    result = await db.execute(select(Post).limit(10))
    posts = result.scalars().all()
    return posts

@app.post("/posts")
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    db_post = Post(**post.dict())
    db.add(db_post)
    # Commit handled automatically by dependency
    # But can explicit commit if needed:
    # await db.commit()
    # await db.refresh(db_post)
    return db_post

# ✅ Prefer SQL aggregation over Python
@app.get("/posts-with-authors")
async def get_posts_with_authors(db: AsyncSession = Depends(get_db)):
    # Use SQL joins and json_build_object for complex responses
    query = """
        SELECT json_build_object(
            'post', p.*,
            'author', u.*
        ) FROM post p JOIN user u ON p.user_id = u.id
    """
    result = await db.execute(query)
    return result.all()
```

**Rules:**
- Inject `AsyncSession` via `Depends(get_db)`
- All queries require `await` (execute, commit, refresh, rollback)
- Dependency auto-commits on success, rollbacks on exception
- Prefer SQL-level operations (joins, aggregations) over Python loops
- FastAPI caches dependencies per request (same session in multiple deps)

---

## Step 5: Configure Alembic for Migrations

```bash
# Initialize Alembic
alembic init migrations
```

```ini
# alembic.ini - Human-readable migration filenames
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
```

```python
# migrations/env.py
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base  # Import all models

target_metadata = Base.metadata

async def run_async_migrations():
    connectable = create_async_engine(DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        await connection.commit()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
```

```bash
# Create migration with descriptive slug
alembic revision --autogenerate -m "add_user_email_index"
# Generates: 2025-12-27_add_user_email_index.py

# Apply migrations
alembic upgrade head
```

**Rules:**
- Migrations MUST be static and revertable
- Use human-readable filenames (YYYY-MM-DD_description.py)
- Import ALL models in env.py for autogenerate to work
- Migrations run with async engine via `run_sync()`
- Never modify committed migrations; create new ones

---

## Quick Checklist

- [ ] Async engine created with `create_async_engine()` and `postgresql+asyncpg://`
- [ ] Naming conventions defined in metadata
- [ ] Session factory uses `expire_on_commit=False`
- [ ] Dependency function yields session with try/except/finally
- [ ] All models use singular, lowercase, snake_case table names
- [ ] Datetime columns end with `_at`, date columns with `_date`
- [ ] All route handlers use `db: AsyncSession = Depends(get_db)`
- [ ] All database operations use `await`
- [ ] Alembic configured with human-readable file template
- [ ] Prefer SQL operations (joins, aggregations) over Python loops
