# Python Best Practices Guide

**Purpose:** Use this guide when writing or reviewing Python code to ensure consistency, readability, and maintainability.

## Overall Pattern

Python code prioritizes **readability** and **explicitness** (PEP 20). Follow these conventions:
- Consistent naming: `snake_case` for functions/variables, `CapWords` for classes
- Organized imports: system → third-party → local
- Comprehensive docstrings for public APIs
- Prefer built-in patterns (comprehensions, context managers) over manual implementations

---

## Step 1: Naming Conventions

```python
# Variables, functions, methods, modules
user_profile = "John"
def calculate_total(items):
    pass

# Classes and Exceptions
class UserProfile:
    pass
class ValidationError(Exception):
    pass

# Protected (internal use)
def _internal_helper():
    pass

# Private (name mangling)
def __private_method():
    pass

# Constants
MAX_RETRIES = 3
API_TIMEOUT = 30
```

**Rules:**
- Avoid single letters (`l`, `O`, `I` especially)
- Remove redundant prefixes: `audio.Core()` not `audio.AudioCore()`
- Use reverse notation: `elements_active` not `active_elements`
- Constants always `UPPER_SNAKE_CASE`

---

## Step 2: Code Style Patterns

```python
# Equality checks - prefer truthiness
if attr:
    process()
if not attr:
    skip()
if attr is None:
    handle_none()

# AVOID
if attr == True:  # Wrong
    pass

# List comprehensions over loops
filtered = [i for i in items if i > 4]
squared = [x**2 for x in range(10)]

# File handling - always use context managers
with open('data.txt') as f:
    content = f.read()

# Line continuations with parentheses (80-100 chars)
result = (
    "Long string part one "
    "part two "
    "part three"
)
```

**Rules:**
- Use truthiness checks, not `== True/False`
- Always use `with` for file operations
- Prefer comprehensions for simple transformations
- Keep lines under 100 characters
- Use spaces (4) not tabs

---

## Step 3: Import Organization

```python
# 1. System imports
import os
import sys
from pathlib import Path

# 2. Third-party imports
import requests
import numpy as np
from flask import Flask, jsonify

# 3. Local imports
from myapp import models
from myapp.utils import helpers
```

**Rules:**
- Three sections separated by blank lines
- Import full modules when possible: `import canteen.sessions`
- Avoid `from x import y` for functions (prevents circular imports)
- OK for classes: `from flask import Flask`
- Alphabetize within each section

---

## Step 4: Documentation (PEP 257)

```python
def get_user(user_id):
    """Return user object for given ID."""
    pass

class Person:
    """Human representation with basic attributes.

    :param name: Person's full name (str)
    :param age: Person's age in years (int)
    """
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self, formal=False):
        """Generate greeting message.

        :param formal: Use formal greeting style (bool)
        :return: Greeting string (str)
        """
        prefix = "Hello" if formal else "Hi"
        return f"{prefix}, {self.name}"
```

**Rules:**
- Single-line for simple functions: `"""Do something."""`
- Multi-line includes: summary, params with types, return type
- Classes document constructor params
- Prefer readable code over excessive comments

---

## Step 5: Testing Patterns

```python
# Unit test - single functionality
class TestUserProfile:
    def test_full_name_combines_first_and_last(self):
        user = UserFactory(first="John", last="Doe")
        assert user.full_name == "John Doe"

    def test_age_validation_rejects_negative(self):
        with pytest.raises(ValidationError):
            User(age=-5)

# Functional test - user scenario
class TestBlogPostCreation:
    def test_user_can_create_and_publish_post(self):
        # User logs in
        self.client.login(username="author", password="pass")
        # Navigates to new post
        response = self.client.get("/posts/new")
        # Fills form and submits
        self.client.post("/posts/", data={"title": "Test", "body": "Content"})
        # Verifies post appears in list
        assert "Test" in self.client.get("/posts/").content
```

**Rules:**
- Descriptive test names (no docstrings needed)
- Use factories, not fixtures for object creation
- Isolate tests: no real databases/networks
- Incomplete tests: `assert False, "TODO: finish me"`
- Functional tests read as user stories

---

## Quick Checklist

- [ ] All names follow conventions (snake_case, CapWords, CONSTANTS)
- [ ] Imports organized in 3 sections (system, third-party, local)
- [ ] Used truthiness checks (`if attr:` not `if attr == True:`)
- [ ] File operations use `with` statement
- [ ] List operations use comprehensions where appropriate
- [ ] Public functions/classes have docstrings with param/return types
- [ ] Lines under 100 characters
- [ ] Tests are isolated and descriptive
- [ ] No single-letter variables (except i, j in short loops)
- [ ] Code is explicit and readable over clever
