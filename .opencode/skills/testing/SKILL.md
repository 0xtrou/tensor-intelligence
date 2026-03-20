# Skill: testing

Testing conventions for Bittensor Subnet Intelligence System.

## Backend Testing (pytest)
- Framework: `pytest`, `pytest-asyncio`, `pytest-cov`
- Location: `tests/`
- Run: `pytest tests/ -v --cov=src --cov-report=term-missing`
- Conventions:
  - Use `pytest-asyncio` for async tests
  - Mock external APIs (Taostats) in `tests/conftest.py`
  - Database tests use `aiosqlite` for in-memory testing
  - Coverage target: >80% for `src/engine/`

## Frontend Testing (vitest)
- Framework: `vitest`, `@testing-library/react`
- Location: `frontend/src/components/__tests__/` and `frontend/src/lib/__tests__/`
- Run: `npm test` (in `frontend/`)
- Conventions:
  - Use `jsdom` environment
  - Mock API calls in `frontend/src/test/setup.ts`
  - Test component rendering and user interactions
  - Test utility functions in `frontend/src/lib/`

## CI/CD
- GitHub Actions runs tests on every PR
- Coverage reports uploaded to Codecov
- Build verification for Docker images
