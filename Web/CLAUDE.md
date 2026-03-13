# Web – projekt_ws24

## Stack
- Backend: Python, FastAPI
- Frontend: React (Vite)
- Package Manager Python: uv
- Package Manager JS: npm
- Datenbank: siehe `../sql/`
- IDE: JetBrains WebStorm

## Struktur
```
Web/
├── Backend/
│   ├── data/           - Datendateien (Fixtures, Seed-Daten)
│   ├── db/             - Datenbankanbindung / Migrations
│   ├── models/         - SQLAlchemy / Pydantic Modelle
│   ├── routes/         - FastAPI Router (je Ressource eine Datei)
│   ├── scripts/        - Hilfsskripte (DB-Setup, Datenmigration)
│   ├── services/       - Business-Logik (von Routes getrennt)
│   ├── tests/          - pytest Tests
│   ├── utils/          - Hilfsfunktionen
│   ├── app.py          - FastAPI App-Instanz & Middleware
│   ├── config.py       - Konfiguration / Settings
│   ├── db_session.py   - Datenbank-Session-Management
│   ├── cleanup.py      - Cleanup-Hilfsskript
│   ├── .env            - Lokale Umgebungsvariablen (nicht committen!)
│   └── .env.test       - Test-Umgebungsvariablen (nicht committen!)
├── src/
│   ├── assets/         - Bilder, Fonts, statische Ressourcen
│   ├── components/     - Wiederverwendbare UI-Komponenten
│   ├── context/        - React Context / globaler State
│   ├── debug/          - Debug-Hilfsmittel (nicht für Produktion)
│   ├── features/       - Feature-Module (je Feature ein Unterordner)
│   ├── layout/         - Layout-Komponenten (Header, Footer, etc.)
│   ├── AppRouter.jsx   - Routing-Konfiguration
│   ├── index.css       - Globale Styles
│   └── main.jsx        - React Einstiegspunkt
├── public/             - Statische Assets (direkt ausgeliefert)
├── mock/               - Mock-Daten (für Tests/Entwicklung)
├── index.html          - HTML Einstiegspunkt
├── vite.config.js      - Vite Konfiguration
├── pyproject.toml      - Python Projektdefinition
└── uv.lock             - uv Lockfile (committen!)
```

## Backend (FastAPI)
- Virtual Env aktivieren: `.venv\Scripts\activate` (Windows) / `source .venv/bin/activate` (Linux/Mac)
- Dependencies installieren: `uv sync`
- Dev-Server starten: `uv run fastapi dev Backend/app.py`
- Tests ausführen: `uv run pytest Backend/tests/`
- Coverage: `uv run pytest --cov Backend/`

## Frontend (React + Vite)
- Dependencies installieren: `npm install`
- Dev-Server starten: `npm run dev`
- Build: `npm run build`

## Architektur Backend
- Neue Endpunkte: Route in `routes/` anlegen, Business-Logik in `services/`
- Datenbankmodelle in `models/`, Session-Handling über `db_session.py`
- Umgebungsvariablen über `config.py` lesen (nie direkt `os.environ`)

## Coding Conventions
- Python: PEP 8, Type Hints auf allen Funktionen und Routen
- FastAPI: Pydantic-Modelle für alle Request/Response Bodies
- React: Funktionale Komponenten, keine Klassen-Komponenten
- Neue API-Endpunkte immer mit Pydantic-Schema dokumentieren

## Kritische Hinweise
- `.venv/` niemals committen
- `.env` und `.env.test` niemals committen
- `uv.lock` IMMER committen
- DB-Schema Änderungen immer mit `../sql/` synchron halten
- `htmlcov/`, `.coverage` und `__pycache__/` nicht committen
