#!/bin/bash
set -e

# ──────────────────────────────────────────────
# CropScience — project runner
# ──────────────────────────────────────────────

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# ── 1. Start the database ────────────────────
echo "Starting PostgreSQL …"
docker compose up -d --wait

# ── 2. Create virtual environment if missing ──
if [ ! -d "venv" ]; then
    echo "Creating virtual environment …"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# ── 3. Install dependencies ──────────────────
echo "Installing dependencies …"
pip install -q -r requirements.txt

# ── 4. Run migrations ────────────────────────
echo "Running migrations …"
python manage.py migrate

# ── 5. Seed default data ─────────────────────
echo "Seeding default data …"
python manage.py seed_data

# ── 6. Start the dev server ──────────────────
echo "Starting dev server at http://localhost:8000"
python manage.py runserver
