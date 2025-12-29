---
description: Prime agent with codebase understanding
---

# Prime: Load Project Context

## Objective

Build comprehensive understanding of the codebase by analyzing structure, documentation, and key files.

## Process

### 1. Analyze Project Structure

List project files using Glob tool to search for common patterns:
- Source files: `**/*.py`, `**/*.ts`, `**/*.js`, `**/*.tsx`, `**/*.jsx`
- Config files: `**/*.json`, `**/*.yaml`, `**/*.yml`, `**/*.toml`
- Documentation: `**/*.md`, `**/*.rst`

Optionally, if in a git repository, list tracked files:
!`git ls-files` (skip if not a git repo)

Show directory structure:
- Use Bash `ls -R` or equivalent to explore structure
- On Linux/Mac with tree: `tree -L 3 -I 'node_modules|__pycache__|.git|dist|build'`
- On Windows: `tree /F` or use PowerShell `Get-ChildItem -Recurse`

### 2. Read Core Documentation

- Read .agents/PRD.md
- Read CLAUDE.md or similar global rules file
- Read README files at project root and major directories
- Read any architecture documentation

### 3. Identify Key Files

Based on the structure, identify and read:
- Main entry points (main.py, index.ts, app.py, etc.)
- Core configuration files (pyproject.toml, package.json, tsconfig.json)
- Key model/schema definitions
- Important service or controller files

### 4. Understand Current State

If in a git repository, check recent activity:
!`git log -10 --oneline` (skip if not a git repo)

If in a git repository, check current branch and status:
!`git status` (skip if not a git repo)

Otherwise, check file modification times and recent changes through file inspection.

## Output Report

Provide a concise summary covering:

### Project Overview
- Purpose and type of application
- Primary technologies and frameworks
- Current version/state

### Architecture
- Overall structure and organization
- Key architectural patterns identified
- Important directories and their purposes

### Tech Stack
- Languages and versions
- Frameworks and major libraries
- Build tools and package managers
- Testing frameworks

### Core Principles
- Code style and conventions observed
- Documentation standards
- Testing approach

### Current State
- Active branch
- Recent changes or development focus
- Any immediate observations or concerns

**Make this summary easy to scan - use bullet points and clear headers.**
