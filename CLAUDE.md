# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A PhD-project application for conducting and analyzing VR studies on surgical instrument handover. Two subsystems:
- **Unity** – multiplayer VR application (C#, built with Rider)
- **Web** – study management & data analysis platform (Python/FastAPI backend + React/Vite frontend, built with WebStorm)

Database: PostgreSQL (schema in `sql/schema.sql`)

---

## Web — Commands

All commands run from `Web/`.

### Backend (FastAPI + uv)
```bash
uv sync                                  # install Python dependencies
uv run fastapi dev Backend/app.py        # start dev server (port 5000)
uv run pytest Backend/tests/             # run all tests
uv run pytest Backend/tests/test_foo.py  # run a single test file
uv run pytest Backend/tests/test_foo.py::test_name  # run single test
uv run pytest --cov Backend/             # with coverage report
```

Tests require a `.env.test` file in `Web/Backend/` pointing to `DB_NAME=testdb`. The `conftest.py` fixture verifies the target DB is `testdb` before any test runs and cleans the DB before/after each test function.

### Frontend (React + Vite)
```bash
npm install      # install JS dependencies
npm run dev      # start dev server (proxies /api → http://127.0.0.1:5000)
npm run build    # production build
npm run lint     # ESLint
```

---

## Web — Architecture

### Backend layers (in `Web/Backend/`)
| Layer | Location | Purpose |
|---|---|---|
| Routes | `routes/` | FastAPI routers, one file per resource |
| Services | `services/` | Business logic, called by routes |
| DB repositories | `db/` | SQLAlchemy query functions |
| Models | `models/` | SQLAlchemy ORM models + Pydantic schemas |
| Session | `db_session.py` | Engine + `SessionLocal`; auto-selects `.env` vs `.env.test` |
| App entry | `app.py` | FastAPI instance, CORS, lifespan (creates tables, starts cleanup) |

Routes are registered dynamically in `routes/__init__.py::register_routes` — any module with a `router` attribute is included automatically.

### Domain model (key entities)
`Study → Experiment → Trial → TrialSlot → TrialSlotStimulus`
`Trial → TrialParticipantSlot → Participant`
`Trial → Handover → EyeTracking`
`Questionnaire → QuestionnaireItem → QuestionnaireResponse`
`StimulusType → Stimulus → StimulusCombination`
`AreaOfInterest`, `AvatarVisibility` (static/seed data)

### Frontend (in `Web/src/`)
- `AppRouter.jsx` — all routes defined here; main admin paths are under `/study/:studyId/...`
- `features/` — feature-per-folder (study, experiment, participant, questionnaire, Analysis, overview, configuration, shared)
- `@` alias maps to `src/`
- UI: MUI + Ant Design + Tailwind CSS; charts: Recharts, Chart.js, ApexCharts, Plotly
- Vite dev proxy forwards `/api/*` to FastAPI at port 5000

### Data import scripts (`Web/Backend/scripts/`)
Used to seed the database from JSON files in `Web/Backend/data/static/`. Entry point: `manage_imports.py`.

---

## Git Conventions

- Feature branches: `feature/description`
- Bugfix branches: `fix/description`
- Commit messages in English, short and precise
- No direct push to `main`

---

## Database

- Schema source of truth: `sql/schema.sql` (PostgreSQL 17)
- SQLAlchemy ORM mirrors the schema via models in `Web/Backend/models/`
- Schema changes must be reflected in both `sql/` and the ORM models; verify Unity API compatibility

---

## Unity

See `Unity/CLAUDE.md` for Unity-specific conventions.
Key rules:
- Rename assets only via the Unity Editor
- Always commit `.meta` files alongside their asset
- Never touch `Library/`, `Temp/`, `obj/`
- C# conventions: PascalCase for classes/methods, `_camelCase` for private fields, prefer `[SerializeField]` over public fields

---

## Critical Rules

- `.env` and `.env.test` must never be committed
- `uv.lock` must always be committed
- Read config via `config.py` / `db_session.py`, never `os.environ` directly in route/service code
- New API endpoints need Pydantic request/response models
- DB schema changes: update `sql/schema.sql` + ORM models + check Unity API compatibility
