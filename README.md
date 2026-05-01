# Collaborative Manual Tasks in Distributed Virtual Environments

A PhD research project investigating multisensory feedback strategies for collaborative object handovers in VR. Two participants wearing VR headsets share a virtual workspace and pass surgical instruments to each other while different visual, auditory, and tactile feedback conditions are applied. The goal is to identify which feedback combinations best support safe and effective handovers.

---

## Repository Structure

```
projekt_ws24/
├── Unity/          VR application (C#, Photon Fusion, OpenXR)
├── Web/            Study management & analysis platform (Python/FastAPI + React)
├── sql/            PostgreSQL database schema
└── notebooks/      Data analysis notebooks (Jupyter, planned)
```

| Subsystem | Description | README |
|---|---|---|
| **Unity** | Multiplayer VR app — runs on two Meta Quest headsets simultaneously | [Unity/README.md](Unity/README.md) |
| **Web** | Browser-based platform for configuring studies, controlling sessions, and analysing results | [Web/README.md](Web/README.md) |
| **SQL** | Database schema reference — all tables with descriptions | [sql/README.md](sql/README.md) |
| **Notebooks** | Jupyter notebooks for statistical analysis and visualisation of study data | [notebooks/README.md](notebooks/README.md) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Unity VR Application (×2 headsets)                         │
│  Photon Fusion (multiplayer) · OpenXR · Meta Quest          │
│  Reports handover events and eye tracking via REST          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│  Web Backend  (FastAPI · Python 3.12 · port 5000)           │
│  Business logic · REST API · DB access via SQLAlchemy       │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQLAlchemy / psycopg2
┌──────────────────────▼──────────────────────────────────────┐
│  PostgreSQL 17  (port 5432)                                  │
│  Studies · Experiments · Trials · Handovers · Eye Tracking  │
└─────────────────────────────────────────────────────────────┘
                       ▲
                       │ REST API  (/api → port 5000)
┌──────────────────────┴──────────────────────────────────────┐
│  Web Frontend  (React · Vite · port 5173)                   │
│  Study configuration · Live session control · Analysis UI   │
└─────────────────────────────────────────────────────────────┘
```

**Data flow during a study session:**

1. Researcher configures a study (stimuli, questionnaires, participant slots) in the web frontend.
2. The Unity application polls the backend for the active experiment and loads the assigned stimulus configuration.
3. During the trial, Unity sends handover events and eye tracking fixations to the backend in real time.
4. After each trial, participants fill in questionnaires via the web frontend.
5. After the study, the researcher accesses the analysis section to review results and export data.

---

## Quick Start

See [Web/README.md](Web/README.md) for full setup and start instructions. The short version:

```bash
# Windows — one-time setup
Web\setup_windows.bat

# macOS — one-time setup
chmod +x Web/setup_mac.sh && ./Web/setup_mac.sh

# Start both backend and frontend
Web\start_windows.bat      # Windows
./Web/start_mac.sh         # macOS
```

Open **http://localhost:5173** in your browser.

---

## Tech Stack

| Layer | Technology |
|---|---|
| VR Runtime | Unity, C#, Photon Fusion 2 (Shared Mode), OpenXR |
| Backend | Python 3.12, FastAPI, SQLAlchemy, uv |
| Frontend | React, Vite, MUI, Ant Design, Tailwind CSS |
| Database | PostgreSQL 17 |
| Charts | Recharts, Chart.js, ApexCharts, Plotly |
