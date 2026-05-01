#!/bin/bash
set -e

echo "============================================"
echo " VR Study Management - Setup (macOS)"
echo "============================================"
echo ""

# Install Homebrew if not present
if ! command -v brew &>/dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo "[OK] Homebrew installed."
    echo ""
else
    echo "[OK] Homebrew found."
    echo ""
fi

# Install required tools
echo "[1/4] Installing Python 3.12..."
brew install python@3.12 || true
echo ""

echo "[2/4] Installing uv..."
brew install uv || true
echo ""

echo "[3/4] Installing Node.js..."
brew install node || true
echo ""

echo "[4/4] Installing PostgreSQL 17..."
brew install postgresql@17 || true
brew link postgresql@17 --force 2>/dev/null || true
echo ""

# Start PostgreSQL service
echo "Starting PostgreSQL service..."
brew services start postgresql@17
sleep 3
echo "[OK] PostgreSQL service started."
echo ""

# Collect database credentials
# On macOS with Homebrew, the default superuser is the current system user (no password needed)
CURRENT_USER=$(whoami)
echo "Please enter your PostgreSQL connection details."
echo "(Press Enter to accept the default value shown in brackets)"
echo ""

read -p "Database host [localhost]: " DB_HOST
DB_HOST="${DB_HOST:-localhost}"

read -p "Database port [5432]: " DB_PORT
DB_PORT="${DB_PORT:-5432}"

read -p "Database name [vr_study]: " DB_NAME
DB_NAME="${DB_NAME:-vr_study}"

read -p "Database user [$CURRENT_USER]: " DB_USER
DB_USER="${DB_USER:-$CURRENT_USER}"

read -s -p "Database password (leave empty for default Homebrew setup): " DB_PASSWORD
echo ""
echo ""

# Create database (ignore error if it already exists)
echo "Creating database \"$DB_NAME\"..."
if [ -n "$DB_PASSWORD" ]; then
    PGPASSWORD="$DB_PASSWORD" createdb -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" "$DB_NAME" 2>/dev/null \
        || echo "(Database already exists, continuing...)"
else
    createdb -U "$DB_USER" "$DB_NAME" 2>/dev/null \
        || echo "(Database already exists, continuing...)"
fi
echo "[OK] Database ready."
echo ""

# Write .env file
ENV_FILE="Backend/.env"
cat > "$ENV_FILE" <<EOF
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
EOF

echo "[OK] Configuration written to Backend/.env"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
uv sync
echo "[OK] Python dependencies installed."
echo ""

# Install JS dependencies
echo "Installing JavaScript dependencies..."
npm install
echo "[OK] JavaScript dependencies installed."
echo ""

# Create database tables
echo "Creating database tables..."
uv run python -c "import Backend.models; from Backend.db_session import engine; Backend.models.Base.metadata.create_all(bind=engine)"
echo "[OK] Database tables created."
echo ""

# Import required static data
echo "Importing required static data..."
cd Backend/scripts
uv run python import_static_data.py
cd ../..
echo "[OK] Static data imported."
echo ""

echo "============================================"
echo " Setup complete!"
echo " Run ./start_mac.sh to launch the app."
echo "============================================"
