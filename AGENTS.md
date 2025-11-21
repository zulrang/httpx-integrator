# AI Agent Development Guide

This guide provides AI agents with essential information for working on the codebase efficiently.

## Quick Start Checklist

Before starting development, ensure:

- [ ] Repository cloned: `git clone <repo-url>`
- [ ] Dependencies installed: `uv sync --all-groups`
- [ ] Environment configured: Copy `.env.example` to `.env`
- [ ] Docker running: Check with `just check-docker`

## Essential Commands

### Development

```bash
# Start local development environment
just start
```

### Quality Assurance

```bash
# Run all QA checks (lint, type check, import guards)
just check

# Format code
just lint

# Type checking
just type
```

### Testing

```bash
# Run all tests with coverage
just test

# Run unit tests only (no docker needed)
uv run pytest tests/unit

# Run specific test file
uv run pytest tests/unit/test_something.py

# Run specific test function
uv run pytest tests/unit/test_something.py::test_function_name

# Run with verbose output
uv run pytest -vv tests/unit/test_something.py
```

## Project Structure

```
httpx-integrator/
├── src/httpx_integrator/              # Source code
├── tests/                    # Tests (mirrors src structure)
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── scripts/                  # Helper scripts
├── docs/                     # Documentation
```

## Coding Guidelines

### Style

- Python 3.12+ syntax
- 4-space indentation
- 120-character line length
- PEP 8 compliance
- Type hints required

### Testing

- Use real in-memory adapters over mocks
- **Function-based tests ONLY** - Never use class-based tests
- All tests must be standalone functions (e.g., `def test_something():`)
- Never create test classes (e.g., `class TestSomething:`)
- Maintain or improve code coverage

### Architecture

- Redis used for caching
- Domain-driven design, hexagonal architecture

## Common Workflows

### Adding a New Feature

```bash
# 1. Write code in src/
# 2. Write tests in tests/
# 3. Run QA and tests
just check

# 6. Commit
git add .
git commit -m "Add feature XYZ"
git push origin feature-xyz

# 7. Create PR on GitHub
```

### Fixing a Bug

```bash
# 1. Write failing test first
# tests/unit/test_something.py

# 2. Fix the bug
# src/traidup/module/file.py

# 3. Verify test passes
uv run pytest tests/unit/test_something.py

# 5. Run full test suite
just test

# 6. Commit and push
git add .
git commit -m "Fix bug #123: Description"
git push origin fix-bug-123
```

### Refactoring Code

```bash
# 1. Ensure tests pass before refactoring
just test

# 2. Make refactoring changes
# 3. Ensure tests still pass
just test

# 4. Run QA checks
just qa

# 5. Commit and push
git add .
git commit -m "Refactor XYZ for better performance"
git push origin refactor-xyz
```

## Important Configuration Files

### Environment Variables

`.env` - Local environment configuration (not committed)
```bash
# Redis
CACHE_HOST=localhost
CACHE_PORT=6379
```

- `pyproject.toml` - Project metadata, dependencies, tool configs
- `uv.lock` - Locked dependency versions
- `.python-version` - Python version specification

## Best Practices for AI Agents

### 1. Test Before Committing

```bash
just check
```

### 2. Use Descriptive Branch Names

```bash
# Good
fix-authentication-token-expiry
feature-add-notification-preferences
refactor-repository-pattern

# Bad
fix
test
tmp
```

### 3. Keep Commits Focused

- One logical change per commit
- Clear commit messages
- Reference issue numbers: `Fix #123: Description`

### 4. Clean Up After Yourself

Update AGENTS.md and CHANGELOG.md as needed.

### 5. Check Dependencies

If you modify dependencies:

```bash
# Add package
uv add package-name

# Add dev dependency
uv add --dev package-name

# Sync all packages
uv sync --all-groups
```

### 6. Follow Repository Guidelines

See `.cursorrules` for comprehensive guidelines on:
- Testing patterns
- Dependency injection
- Repository operations
- Commit guidelines
- And more

## Getting Help

1. Check documentation in `docs/` directory
2. Review `.cursorrules` for repository guidelines
3. Check existing tests for usage examples
4. Review similar implementations in the codebase
5. Consult git history: `git log --follow path/to/file`

---

**Remember:** This is a real production codebase. Always test thoroughly, follow guidelines, and maintain code quality.
