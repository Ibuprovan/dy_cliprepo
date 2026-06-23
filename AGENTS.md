# AGENTS.md

## Project Overview

抖音收藏 AI 知识库 — local tool that scrapes Douyin (TikTok China) bookmarks via Playwright, summarizes with AI, and provides semantic search. Windows-first.

Two independent apps: Python FastAPI backend (port 8000) + React/Vite frontend (port 5173).

## Critical: Windows Asyncio Quirk

**Always use `run_server.py`** to start the backend on Windows, not bare `uvicorn`. Playwright needs `ProactorEventLoop` to spawn child processes; `SelectorEventLoop` (Windows default for some Python versions) fails silently.

```bash
cd backend && python run_server.py
```

Or use `start_backend.bat` which does the same.

## Quick Start

```bash
# Full startup (creates venv, installs deps, launches both)
start.bat

# Backend only
start_backend.bat

# Frontend only
start_frontend.bat

# First-time Douyin login (required before sync)
login.bat
# or: cd backend && python login_manual.py
```

## Dev Commands

### Backend
```bash
cd backend
python -m venv venv          # create venv (if missing)
venv\Scripts\activate        # activate
pip install -r requirements.txt
playwright install chromium  # browser binary (one-time)
python run_server.py         # start server (port 8000)
```

Only 4 dependencies: fastapi, uvicorn, playwright, pydantic.

### Frontend
```bash
cd frontend
npm install
npm run dev                  # Vite dev server (port 5173)
npm run build                # tsc + vite build
npm run lint                 # eslint
```

## Architecture Notes

- **Backend entry**: `backend/app/main.py` → FastAPI app
- **Config**: `backend/app/core/config.py` — all paths derived from project root, never hardcoded
- **Data storage**: JSON files in `backend/data/` (not SQLite yet despite README claims)
  - `douyin_auth.json` — Playwright storage_state (login cookies)
  - `videos.json` — synced video data
  - `sync_progress.json` — task progress
- **Auth file**: code uses `douyin_auth.json`, some docs reference `auth.json` — trust the code
- **Frontend**: currently a single-file MVP (`frontend/src/App.tsx`), uses inline styles not Tailwind despite being a devDependency
- **Vite proxy**: `/api` and `/health` requests proxy to `localhost:8000` in dev

## Gotchas

- **No test framework**: no pytest config, no test script in package.json. `backend/test_*.py` files are manual diagnostic scripts, not automated tests.
- **No CI/CD**: no GitHub Actions or similar configured.
- **Data dir is gitignored**: `backend/data/` contents won't be in repo. First run creates dirs automatically via `ensure_dirs()`.
- **Playwright browsers**: must run `playwright install chromium` after venv setup. Browser binaries are not in the repo.
- **Login expires**: Douyin cookies last ~7 days. Re-run `login.bat` when sync fails with auth errors.
- **README is stale**: describes SQLite/ChromaDB/AI features not yet implemented. Current MVP uses JSON storage and has no AI integration.
