@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  VR Study Management - Setup (Windows)
echo ============================================
echo.

:: Check winget
where winget >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] winget not found.
    echo Please update Windows or install "App Installer" from the Microsoft Store.
    pause
    exit /b 1
)
echo [OK] winget found.
echo.

:: Collect credentials before installing anything
echo Please enter your desired PostgreSQL configuration.
echo (Press Enter to accept the default value shown in brackets)
echo.

set /p DB_HOST="Database host [localhost]: "
if "!DB_HOST!"=="" set DB_HOST=localhost

set /p DB_PORT="Database port [5432]: "
if "!DB_PORT!"=="" set DB_PORT=5432

set /p DB_NAME="Database name [vr_study]: "
if "!DB_NAME!"=="" set DB_NAME=vr_study

set /p DB_USER="Database user [postgres]: "
if "!DB_USER!"=="" set DB_USER=postgres

set /p DB_PASSWORD="Database password (will also be set as PostgreSQL superuser password): "

echo.

:: Install Python
echo [1/4] Installing Python 3.12...
winget install --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
echo.

:: Install uv
echo [2/4] Installing uv...
winget install --id astral-sh.uv --silent --accept-source-agreements --accept-package-agreements
echo.

:: Install Node.js
echo [3/4] Installing Node.js LTS...
winget install --id OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
echo.

:: Install PostgreSQL (silent, sets superuser password)
echo [4/4] Installing PostgreSQL 17...
winget install --id PostgreSQL.PostgreSQL.17 --silent --accept-source-agreements --accept-package-agreements --override "--mode unattended --superpassword !DB_PASSWORD! --serverport !DB_PORT!"
echo.

:: Refresh PATH from registry so newly installed tools are available
echo Refreshing environment variables...
powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')" > "%TEMP%\_newpath.txt"
set /p NEW_PATH= < "%TEMP%\_newpath.txt"
del "%TEMP%\_newpath.txt"
set "PATH=!NEW_PATH!"
echo [OK] PATH updated.
echo.

:: Wait for PostgreSQL service to be ready
echo Waiting for PostgreSQL to start...
timeout /t 6 /nobreak >nul

:: Create database (ignore error if it already exists)
echo Creating database "!DB_NAME!"...
set PGPASSWORD=!DB_PASSWORD!
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U !DB_USER! -h !DB_HOST! -p !DB_PORT! -c "CREATE DATABASE \"!DB_NAME!\";" 2>nul
echo [OK] Database ready.
echo.

:: Write .env file
set ENV_FILE=Backend\.env
echo DB_HOST=!DB_HOST!> "!ENV_FILE!"
echo DB_PORT=!DB_PORT!>> "!ENV_FILE!"
echo DB_NAME=!DB_NAME!>> "!ENV_FILE!"
echo DB_USER=!DB_USER!>> "!ENV_FILE!"
echo DB_PASSWORD=!DB_PASSWORD!>> "!ENV_FILE!"
echo [OK] Configuration written to Backend\.env
echo.

:: Install Python dependencies
echo Installing Python dependencies...
uv sync
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    echo Tip: If uv is not found, restart this script in a new terminal window.
    pause
    exit /b 1
)
echo [OK] Python dependencies installed.
echo.

:: Install JS dependencies
echo Installing JavaScript dependencies...
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install JavaScript dependencies.
    echo Tip: If npm is not found, restart this script in a new terminal window.
    pause
    exit /b 1
)
echo [OK] JavaScript dependencies installed.
echo.

:: Create database tables
echo Creating database tables...
uv run python -c "import Backend.models; from Backend.db_session import engine; Backend.models.Base.metadata.create_all(bind=engine)"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create database tables. Check your database connection.
    pause
    exit /b 1
)
echo [OK] Database tables created.
echo.

:: Import required static data
echo Importing required static data...
cd Backend\scripts
uv run python import_static_data.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to import static data.
    cd ..\..
    pause
    exit /b 1
)
cd ..\..
echo [OK] Static data imported.
echo.

echo ============================================
echo  Setup complete!
echo  Run start_windows.bat to launch the app.
echo ============================================
echo.
pause
