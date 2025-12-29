# FastAPI Best Practices Guide

**Use this guide when:** Building or refactoring FastAPI applications for optimal performance and maintainability.

## Overall Pattern

```
FastAPI App Structure (Performance-First)
├── Install: uvloop + httptools (async boost)
├── Lifespan: State management via context manager
├── Routes: Always async handlers
├── Dependencies: Async to avoid thread pool
├── WebSockets: async for pattern
└── Tests: AsyncClient (preserve async behavior)
```

FastAPI runs on an async event loop. Every sync operation consumes limited thread pool resources (default: 40 threads). Go async everywhere to maximize throughput.

---

## Step 1: Setup for Maximum Performance

```bash
# Install performance dependencies
pip install "uvicorn[standard]"  # includes uvloop + httptools
```

```python
# For cross-platform projects, add to requirements.txt:
uvloop; sys_platform != 'win32'
httptools
```

**Rules:**
- uvloop provides 2-4x faster event loop (Unix only)
- httptools speeds up HTTP parsing
- Uvicorn auto-detects and uses them if installed
- Enable debug mode in development: `PYTHONASYNCIODEBUG=1` (warns on blocking ops >100ms)

---

## Step 2: Use Lifespan State (Not app.state)

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict
from httpx import AsyncClient
from fastapi import FastAPI, Request

class AppState(TypedDict):
    http_client: AsyncClient
    db_pool: Any  # your database pool type

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[AppState]:
    """Manages application lifecycle resources"""
    async with AsyncClient() as client:
        db_pool = await init_db_pool()
        try:
            yield {"http_client": client, "db_pool": db_pool}
        finally:
            await db_pool.close()

app = FastAPI(lifespan=lifespan)

# Access in routes via request.state
async def get_data(request: Request):
    client = request.state.http_client
    return await client.get("https://api.example.com/data")
```

**Rules:**
- Lifespan state is ASGI-compliant (app.state is FastAPI-specific)
- Type your state dict for IDE autocomplete
- Use context managers for auto-cleanup
- Access via `request.state.{key}`

---

## Step 3: Always Use Async Route Handlers

```python
# ❌ AVOID - Consumes thread pool
@app.get("/users")
def get_users():
    return {"users": [...]}

# ✅ CORRECT - Runs in event loop
@app.get("/users")
async def get_users():
    return {"users": [...]}

# ❌ AVOID - Sync dependency blocks threads
def get_db(request: Request):
    return request.state.db_pool

# ✅ CORRECT - Async dependency
async def get_db(request: Request):
    return request.state.db_pool
```

**Rules:**
- Make every handler `async def` (even if no await inside)
- Make all dependencies async
- Only 40 threads available in default pool
- Sync functions run in thread pool = bottleneck

---

## Step 4: WebSocket Pattern with Async For

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # ✅ CORRECT - Auto-handles disconnects
    async for message in websocket.iter_text():
        await websocket.send_text(f"Echo: {message}")

    # ❌ AVOID - Manual disconnect handling needed
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(data)
```

**Rules:**
- Use `async for` iterators (iter_text, iter_json, iter_bytes)
- Disconnects handled automatically
- No try/except WebSocketDisconnect needed
- Cleaner, more Pythonic code

---

## Step 5: Test with AsyncClient (Not TestClient)

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.fixture
def anyio_backend():
    return "asyncio"  # Avoid running tests twice with trio

@pytest.mark.anyio
async def test_get_users():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/users")
        assert response.status_code == 200
        assert "users" in response.json()
```

**Rules:**
- TestClient blocks async code execution
- AsyncClient preserves async behavior
- Use `pytest.mark.anyio` (AnyIO already in Starlette)
- Set `anyio_backend` fixture to avoid duplicate test runs
- Use `asgi-lifespan` package for lifespan event testing

---

## Quick Checklist

- [ ] Install uvloop and httptools for performance boost
- [ ] Define lifespan context manager with TypedDict state
- [ ] All route handlers are `async def`
- [ ] All dependencies are `async def`
- [ ] WebSockets use `async for websocket.iter_*()`
- [ ] Tests use AsyncClient, not TestClient
- [ ] Tests marked with `@pytest.mark.anyio`
- [ ] Enable `PYTHONASYNCIODEBUG=1` during development
- [ ] Avoid BaseHTTPMiddleware (use pure ASGI middleware)
- [ ] Access shared state via `request.state`, not `app.state`
