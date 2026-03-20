# TENSOR INTELLIGENCE

> Bittensor Subnet Intelligence System -- AI-powered signal generation with resonance visualization

[![CI](https://github.com/0xtrou/tensor-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/0xtrou/tensor-intelligence/actions/workflows/ci.yml)
![Backend Coverage](badges/backend.svg)
![Frontend Coverage](badges/frontend/coverage.svg)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)

## Overview

Tensor Intelligence monitors Bittensor subnet ecosystem via Taostats flow data, applies the Durbin Framework for fundamental analysis, risk assessment, and trend alignment to produce actionable investment signals: **BUY / ACCUMULATE / HOLD / REDUCE / AVOID**.

The debugger-style signal flow visualization shows how each analysis stage contributes to the final signal, with resonance indicators between stages confirming or contradicting the thesis.

## Architecture

```
  +---------------+     +-------------------+     +---------------+
  |  Taostats     |     |  Data Collector   |     |  PostgreSQL    |
  |  Flow API     |---->|  (15min cycle)    |---->|  + Redis       |
  +---------------+     +--------+----------+     +-------+-------+
                                 |                        |
                                 v                        v
                        +----------------+          +---------------+
                        |  Analysis      |          |  FastAPI      |
                        |  Pipeline      |<---------|  REST API     |
                        |                |          |  :8000        |
                        |  +-----------+ |          +-------+-------+
                        |  |Flow Detect| |                  |
                        |  +-----------+ |                  v
                        |  |Durbin     | |          +---------------+
                        |  |Fundamental| |          |  React SPA    |
                        |  +-----------+ |          |  Terminal UX  |
                        |  |Risk Score | |          |  :5173        |
                        |  +-----------+ |          +---------------+
                        |  |Trend Align| |
                        |  +-----------+ |
                        |  |Signal Gen | |
                        |  +-----------+ |
                        +----------------+
```

## Signal Framework

### Pipeline (4 stages)

| Stage | Weight | Description |
|-------|--------|-------------|
| Flow Detection | 35% | EMA analysis on 3d/7d/30d windows -- detects SURGE, STEADY, PEAK, REVERSAL, NEGATIVE |
| Fundamental Analysis | 35% | Durbin Framework -- 7 dimensions (team, use case, execution, network, community, tokenomics, moat) |
| Risk Assessment | 15% | Flow volatility, liquidity, emission sustainability, concentration, crash risk |
| Trend Alignment | 15% | Cross-validation: do flow direction, fundamentals, and risk all agree? |

### Composite Score

```
composite = flow x 0.35 + fundamentals x 0.35 + trend x 0.15 + risk x 0.15
```

### Thresholds

| Signal | Condition | Action |
|--------|-----------|--------|
| BUY | >= 70 | Strong conviction -- build position |
| ACCUMULATE | >= 50 | Moderate conviction -- scale in |
| HOLD | >= 30 | Wait -- insufficient signal |
| REDUCE | >= 15 | Warning -- consider exit |
| AVOID | < 15 | High risk -- stay away |

### Resonance

Between each pipeline stage, a **resonance indicator** shows whether consecutive stages agree:
- **aligned** -- both stages bullish (score >= 50) -- reinforcing signal
- **aligned (bearish)** -- both stages bearish (score < 50) -- negative consensus
- **conflicting** -- stages disagree -- weak signal, caution advised

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Redis |
| Analysis | NumPy, scikit-learn, APScheduler |
| Frontend | React 19, TypeScript, Tailwind CSS v4, Recharts, Vite |
| Infra | Docker Compose, Prometheus, Grafana |

## Quick Start

```bash
# Clone
git clone git@github.com:0xtrou/tensor-intelligence.git
cd tensor-intelligence

# Backend (Python 3.12+)
pip install -e ".[dev]"
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Combined Scripts

From the project root:

```bash
npm start:dev     # backend (uvicorn --reload) + frontend (vite dev) in parallel
npm start:prod    # build frontend, serve from FastAPI on :8000
```

### Docker

```bash
docker compose up -d
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/subnets/` | List all tracked subnets |
| GET | `/subnets/{netuid}` | Subnet detail with recent signals |
| GET | `/subnets/{netuid}/flow` | Flow EMA history |
| GET | `/signals/summary` | Signal type distribution |
| GET | `/signals/top/{n}` | Top N opportunities by score |
| GET | `/signal-flow/{netuid}` | Full pipeline trace with resonance |
| GET | `/reports/` | Generated intelligence reports |

## Testing

```bash
# Backend
pip install -e ".[dev]"
pytest tests/ -v --cov=src --cov-report=term-missing

# Frontend
cd frontend
npm install
npm test
```

## Screenshots

![Dashboard](dashboard-terminal.png)
![Signal Flow](signal-flow-resonance.png)

## License

MIT
