# Skill: frontend

Frontend conventions for Bittensor Subnet Intelligence System.

## Aesthetic (Yggdrasight)
- Terminal-style UX: Dark background, high-contrast accents
- Font: **JetBrains Mono** (primary), SF Mono (fallback)
- Spacing: Tight, grid-based, terminal-like alignment
- Animations: Subtle, pulse-live for real-time data

## Tailwind v4 Theme (frontend/src/index.css)
- **Backgrounds**: `--color-bg` (#0a0a0a), `--color-card` (#161616)
- **Accents**: `--color-accent` (#00ff88), `--color-blue` (#4488ff)
- **Signal Colors**:
  - `BUY`: `--color-buy` (#00ff88)
  - `ACCUMULATE`: `--color-accumulate` (#ffaa00)
  - `HOLD`: `--color-hold` (#888888)
  - `REDUCE`: `--color-reduce` (#ff8844)
  - `AVOID`: `--color-avoid` (#ff4455)

## Component Patterns
- `card-terminal`: Standard container with border and hover effect
- `glow-accent`: Box shadow for highlighted elements
- `tracking-terminal`: Letter spacing for terminal-style text
- `animate-pulse-live`: Pulse effect for live indicators

## Data Visualization
- Use **Recharts** for flow and signal history
- Maintain terminal aesthetic in charts (custom tooltips, grid lines)
- Signal flow visualization in `SignalFlowVisualization.tsx`
