# Skill: project-ctx

Project context for Bittensor Subnet Intelligence System.

## Codebase Structure
- `src/`: Python backend (FastAPI, SQLAlchemy 2.0 async)
  - `api/`: REST endpoints and routes
  - `engine/`: Core logic (analysis, data collection, reports)
  - `models/`: SQLAlchemy database models
  - `db/`: Session management and DB initialization
- `frontend/`: React 19 frontend (TypeScript, Vite, Tailwind v4)
  - `src/components/`: UI components (terminal aesthetic)
  - `src/hooks/`: Custom React hooks
  - `src/api/`: API client and types
- `tests/`: Backend test suite (pytest)
- `Dockerfile` & `docker-compose.yml`: Containerized deployment

## Backend Conventions
- Use **async/await** for all DB and API operations
- Models use SQLAlchemy 2.0 declarative style in `src/models/`
- Business logic belongs in `src/engine/analysis/` or `src/engine/data/`
- Pydantic for request/response validation

## Frontend Conventions
- Functional components with TypeScript
- Tailwind v4 for styling (see `frontend/src/index.css`)
- Recharts for data visualization
- Terminal-style UX (Yggdrasight)

## Key Modules
- `src/engine/analysis/`: Flow detection, Durbin fundamental analysis
- `src/engine/data/`: Taostats API client and data collector
- `frontend/src/components/SignalFlowVisualization.tsx`: Core signal logic UI
