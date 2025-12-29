# FastAPI Reference Guide

**⚠️ LOAD THIS ONLY WHEN WORKING ON FASTAPI TASKS**

This is an on-demand reference for FastAPI development. Do not load unless actively working on FastAPI code.

## Which Guide to Load

Choose ONE guide based on your current task:

### 🚀 [Best Practices Guide](fastapi/fastapi_best_practices_guide.md)
**Use when:** Starting a new project or optimizing performance
- Performance setup (uvloop, httptools)
- Async handlers and dependencies
- Lifespan state management
- WebSocket patterns
- Testing with AsyncClient

### 🗄️ [Database Patterns Guide](fastapi/fastapi_database_patterns.md)
**Use when:** Setting up databases, SQLAlchemy, or migrations
- Async SQLAlchemy 2.0 engine setup
- Session management and dependency injection
- Database naming conventions
- Alembic migrations
- Connection pooling

### 🔐 [Authentication Patterns Guide](fastapi/fastapi_auth_patterns.md)
**Use when:** Implementing login, JWT tokens, or securing endpoints
- OAuth2 + JWT authentication flow
- Argon2 password hashing (2025 standard)
- Token generation and validation
- Protected routes with dependencies
- Role-based access control (RBAC)

### 📁 [Project Structure Guide](fastapi/fastapi_project_structure.md)
**Use when:** Organizing code, creating new features, or refactoring
- Domain-based folder structure
- Router organization with APIRouter
- Service layer pattern (thin routes)
- Schemas vs Models separation
- Cross-domain dependencies

## Task → Guide Mapping

**Only load when actively working on these tasks:**

- New FastAPI project → `fastapi/fastapi_project_structure.md` + `fastapi/fastapi_best_practices_guide.md`
- Adding database → `fastapi/fastapi_database_patterns.md`
- Adding authentication → `fastapi/fastapi_auth_patterns.md`
- Performance issues → `fastapi/fastapi_best_practices_guide.md`
- New feature/domain → `fastapi/fastapi_project_structure.md`

## Core Principles (All Guides)

1. **Async Everywhere** - All handlers, dependencies, database operations
2. **Dependency Injection** - Sessions, auth, validation via Depends()
3. **Thin Routes** - Business logic in services, routes handle HTTP only
4. **SQL-First** - Database handles joins/aggregations, not Python

---

**Remember:** Load the specific detailed guide only when you need it for the current task.
