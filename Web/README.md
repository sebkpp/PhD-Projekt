# VR Study Management — Web Application

## What is this?

This application is the web-based control and analysis platform for a research project investigating **virtual object handovers in VR**. In the underlying VR application (built in Unity), two participants wearing VR headsets interact with each other and hand virtual objects back and forth. This web platform is used to:

- **Plan and configure** studies, experiments, and trials before they take place
- **Monitor and control** live trial sessions (start/stop trials, track participant readiness)
- **Collect data** from the VR application (handover events, eye tracking, questionnaire responses)
- **Analyze results** after the study is complete (statistical analysis, visualizations, data export)

The platform is built for study conductors and researchers — no programming knowledge is required to use it.

---

## Architecture Overview

The application consists of two parts that run simultaneously:

| Component | Technology | Default Port |
|---|---|---|
| **Backend** | Python / FastAPI | `5000` |
| **Frontend** | React / Vite | `5173` |
| **Database** | PostgreSQL 17 | `5432` |

The frontend runs in your browser and communicates with the backend via a REST API. The backend stores all data in a PostgreSQL database and also serves as the interface for the Unity VR application.

---

## Prerequisites

The setup script installs all required software automatically. The following tools will be installed if not already present:

| Software | Purpose | Version |
|---|---|---|
| **Python** | Backend runtime | 3.12+ |
| **uv** | Python package manager | latest |
| **Node.js** | Frontend build tooling | 20+ |
| **PostgreSQL** | Database | 17 |

**Windows:** The script uses `winget`, which is built into Windows 10 and Windows 11. No additional tools are needed before running setup.

**macOS:** The script uses [Homebrew](https://brew.sh/). If Homebrew is not installed, the setup script will install it automatically. You may be prompted for your system password during that step — this is expected.

> **Important:** Run all commands from inside the `Web/` directory unless stated otherwise.

---

## Setup

Run the setup script **once** when setting up the project for the first time. It will:

1. Install Python, uv, Node.js, and PostgreSQL (if not already installed)
2. Ask for your PostgreSQL database credentials
3. Create the configuration file (`Backend/.env`) automatically
4. Install all Python and JavaScript dependencies
5. Create the database tables
6. Import required reference data (stimuli, questionnaires, areas of interest, etc.)

**Windows** — open a terminal (Command Prompt or PowerShell) in the `Web/` folder and run:

```bat
setup_windows.bat
```

**macOS** — open a terminal in the `Web/` folder and run:

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

During setup you will be asked for:

- **Database host** — usually `localhost` (press Enter to accept)
- **Database port** — usually `5432` (press Enter to accept)
- **Database name** — a name for the database, e.g. `vr_study`
- **Database user** — usually `postgres` on Windows, your macOS username on Mac
- **Database password** — the password you want to use (on Windows, this will also be set as the PostgreSQL superuser password)

If the setup script cannot find `uv` or `npm` after installing them, close the terminal, open a new one, and run the script again. This is a known Windows behaviour when newly installed tools are not yet visible in the current session.

---

## Starting the Application

After setup is complete, use the start script to launch both backend and frontend together.

**Windows:**
```bat
start_windows.bat
```

**macOS:**
```bash
./start_mac.sh
```

On Windows, two separate terminal windows will open — one for the backend and one for the frontend. On macOS, both run in the same terminal. Once both are ready, open your browser and go to:

**http://localhost:5173**

The backend API is available at http://localhost:5000 (used internally by the frontend and by the Unity VR application).

To stop the application, close the terminal windows (Windows) or press `Ctrl+C` (macOS).

---

## Alternative: Opening with JetBrains WebStorm

If you have [JetBrains WebStorm](https://www.jetbrains.com/webstorm/) installed, you can open the `Web/` folder directly in WebStorm. After running the setup script at least once (to create `.env` and install dependencies), you can start backend and frontend from within the IDE:

- **Frontend:** Open the `package.json` file and click the green run button next to `"dev"`, or use the built-in npm tool window (`View → Tool Windows → npm`).
- **Backend:** Create a run configuration for `Backend/app.py` using the Python interpreter from the `.venv` folder inside `Web/`. Set the working directory to `Web/`.

WebStorm also provides integrated terminal access, code completion for both Python and JavaScript, and database tooling for connecting to PostgreSQL.

---

## Initial Data

### Required reference data (imported automatically during setup)

The following data is imported from `Backend/data/static/` during setup and is required for the application to work:

- Stimulus types and definitions (the virtual objects used in handover tasks)
- Avatar visibility configurations
- Areas of interest (AOI) for eye tracking analysis
- Questionnaires and questionnaire items

### Optional: Mock / Test Data

A pre-built example dataset is available in `Backend/data/testmock/`. It contains a complete study with experiments, trials, participants, handover events, eye tracking data, and questionnaire responses. This is useful for exploring the application and its analysis features without needing to conduct a real study first.

To import it, run from the `Web/` directory:

```bash
cd Backend/scripts
uv run python manage_imports.py
```

---

## API Documentation

While the backend is running, FastAPI automatically provides interactive API documentation in the browser. No additional setup is required.

| URL | Description |
|---|---|
| http://localhost:5000/docs | **Swagger UI** — interactive, lets you test endpoints directly in the browser |
| http://localhost:5000/redoc | **ReDoc** — clean read-only reference, better for browsing |

The Swagger UI at `/docs` is particularly useful for debugging: you can expand any endpoint, fill in parameters, send a real request, and see the exact response the backend returns. All request and response schemas are documented automatically based on the Pydantic models defined in the backend code.

---

## Accessing the Database (Debugging)

There are several ways to inspect the database contents directly, which is useful for debugging or verifying that data was imported correctly.

### pgAdmin (GUI — recommended for beginners)

pgAdmin is a graphical database browser that is bundled with PostgreSQL on Windows. On macOS it can be installed separately from https://www.pgadmin.org/download/.

1. Open pgAdmin from the Start Menu (Windows) or Applications folder (macOS)
2. In the left panel, expand **Servers → PostgreSQL 17 → Databases → your database name**
3. Right-click any table under **Schemas → public → Tables** and choose **View/Edit Data → All Rows** to inspect its contents
4. Use **Tools → Query Tool** to run custom SQL queries

### psql (Command Line)

`psql` is the built-in PostgreSQL command-line client. It is available in any terminal after PostgreSQL is installed.

Connect to your database:

```bash
psql -U postgres -d vr_study -h localhost
```

Replace `postgres`, `vr_study`, and `localhost` with your actual credentials from `Backend/.env`.

Useful commands inside `psql`:

| Command | Description |
|---|---|
| `\dt` | List all tables |
| `\d table_name` | Show columns of a table |
| `SELECT * FROM table_name LIMIT 10;` | View first 10 rows |
| `\q` | Quit |

### WebStorm Database Tool

If you are using WebStorm, it has a built-in database browser:

1. Open **View → Tool Windows → Database**
2. Click **+** → **Data Source → PostgreSQL**
3. Enter the connection details from `Backend/.env` (host, port, database, user, password)
4. Click **Test Connection** to verify, then **OK**
5. You can now browse tables, run queries, and edit data directly in the IDE

### DBeaver (free, cross-platform alternative)

[DBeaver](https://dbeaver.io/) is a free standalone database GUI that works on both Windows and macOS and supports PostgreSQL. It offers a similar experience to pgAdmin but with a more modern interface. Download from https://dbeaver.io/download/.

---

## Troubleshooting

**Setup script fails at "Creating database tables"**
- Make sure PostgreSQL is running. On Windows, check Services (`Win+R` → `services.msc`) and look for a PostgreSQL service. On macOS, run `brew services list` and check that `postgresql@17` shows as `started`.
- Double-check that the credentials you entered during setup are correct.

**Cannot connect to the database after setup**
- Open `Backend/.env` in a text editor and verify the values for `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`.
- Make sure the database was created. You can check with pgAdmin or by running `psql -U postgres -l` in a terminal.

**Port already in use**
- The backend uses port `5000` and the frontend uses port `5173`.
- If another application is using one of these ports, stop it first, then start the app again.

**`uv` or `npm` not found after setup**
- Close the terminal completely, open a new one, and try running the start script again. Newly installed tools sometimes require a fresh terminal session to be recognized.

**Frontend loads but shows no data**
- Make sure the backend is also running and accessible at http://localhost:5000.
- Check the backend terminal window for error messages.
