# PrizePicks EV Bot

OddsJam-style +EV basketball analyzer for PrizePicks.

Compares PrizePicks player prop lines against sharp sportsbooks (FanDuel, DraftKings, BetMGM, Caesars),
removes the vig to calculate no-vig fair odds, and surfaces statistically profitable picks
with Kelly Criterion bet sizing and market width confidence scoring.

---

## Prerequisites

| Tool | Install |
|---|---|
| Python 3.11+ | [python.org](https://www.python.org/downloads/) |
| uv | See Step 1 below |
| Docker Desktop | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Git | [git-scm.com](https://git-scm.com/) |

---

## Setup (Windows PowerShell)

### Step 1 — Install uv
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Close and reopen PowerShell, then verify:
```powershell
uv --version
```

### Step 2 — Clone and enter the project
```powershell
git clone https://github.com/your-org/prizepicks_ev_bot.git
cd prizepicks_ev_bot
```

### Step 3 — Install all dependencies
```powershell
uv sync --extra dev
```

### Step 4 — Set up your environment file
```powershell
Copy-Item .env.example .env
```
Open `.env` and fill in your `ODDS_API_KEY` from [the-odds-api.com](https://the-odds-api.com).

### Step 5 — Start the database and Redis
Make sure Docker Desktop is running, then:
```powershell
docker compose up -d
docker compose ps
```
Both `ppev_postgres` and `ppev_redis` should show `healthy`.

### Step 6 — Run the smoke tests
```powershell
uv run pytest tests/test_setup.py -v
```
Expected: **6 passed**. If all pass, setup is complete.

### Step 7 — Install pre-commit hooks
```powershell
uv run pre-commit install
```

### Step 8 — Verify the CLI
```powershell
uv run ppev --help
uv run ppev live --min-ev 5 --confidence high
```

---

## Day-to-day Commands

```powershell
uv run ppev live                          # live +EV feed
uv run ppev live --min-ev 5              # only EV > 5%
uv run ppev live --stat points rebounds  # filter by stat
uv run ppev live --confidence high       # high confidence only
uv run ppev history 2025-01-15           # picks from a past date
uv run ppev stats                        # overall hit rate & ROI
uv run ppev bankroll 2500                # update your bankroll

uv run pytest                            # run all tests
uv run pytest --cov=prizepicks_ev_bot --cov-report=html
uv run black .                           # format code
uv run ruff check . --fix                # lint
uv run mypy prizepicks_ev_bot/           # type check

docker compose up -d                     # start DB + Redis
docker compose down                      # stop DB + Redis
```

---

## Project Structure

```
prizepicks_ev_bot/
├── prizepicks_ev_bot/
│   ├── models.py           # Shared Pydantic models (Phase 1)
│   ├── settings.py         # config.yaml + .env loader (Phase 1)
│   ├── logging_config.py   # Structured logging (Phase 1)
│   ├── ingestion/          # API clients — PrizePicks + sharp books (Phase 1)
│   ├── normalization/      # Player name + stat type matching (Phase 2)
│   ├── analytics/          # No-vig math, EV%, Kelly, market width (Phase 3)
│   ├── storage/            # PostgreSQL models + Redis client (Phase 2)
│   ├── scheduler/          # APScheduler pipeline runner (Phase 4)
│   ├── alerts/             # Discord webhook + CSV export (Phase 5)
│   ├── cli/                # Typer + Rich terminal UI (Phase 5)
│   └── backtesting/        # CLV tracking + outcome results (Phase 6)
├── tests/
├── config.yaml             # Tunable parameters (not secrets)
├── docker-compose.yml      # PostgreSQL + Redis
├── .env.example            # Copy to .env and fill in secrets
├── .gitignore
├── .pre-commit-config.yaml
└── pyproject.toml
```

---

## CLI Command
The CLI is registered as `ppev` (short for PrizePicks EV):
```powershell
uv run ppev --help
```

---

## Phase Roadmap

| Phase | Module | Status |
|---|---|---|
| 1 | Odds Ingestion + Data Models | 🟢 Complete |
| 2 | Normalization + Storage | 🟡 In Progress |
| 3 | Analytics Engine | ⬜ Not Started |
| 4 | Scheduler + Automation | ⬜ Not Started |
| 5 | CLI + Discord Alerts | ⬜ Not Started |
| 6 | CLV Tracking + Backtesting | ⬜ Not Started |
