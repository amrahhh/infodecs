# CropScience API

REST API for crop science data management, built with Django and Django REST Framework.

## Features

- **JWT Authentication** — Register, login, logout with token blacklisting
- **Crop Categories** — Full CRUD for organizing crops
- **Crops Management** — CRUD with filtering, search, ordering, and pagination
- **Excel Export** — Export crop data to `.xlsx`
- **Swagger Docs** — Interactive API documentation at `/api/docs/`

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose

### One-Command Setup

```bash
./run.sh
```

This single script will:

1. Start PostgreSQL via Docker Compose
2. Create a virtual environment (if needed)
3. Install dependencies
4. Run database migrations
5. Start the dev server at `http://localhost:8000`

### Manual Setup

```bash
# 1. Start the database
docker compose up -d

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

### Environment Variables

Configure via the `.env` file in the project root:

| Variable            | Default          |
| ------------------- | ---------------- |
| `DB_NAME`           | `infodecs_db`    |
| `DB_USER`           | `infodecs_user`  |
| `DB_PASSWORD`       | `12345`          |
| `DB_HOST`           | `localhost`      |
| `DB_PORT`           | `5432`           |
| `DJANGO_SECRET_KEY` | *(dev key)*      |
| `DJANGO_DEBUG`      | `True`           |

## Docker

The project uses Docker Compose to run PostgreSQL. The database, user, and password are created automatically from the `.env` file on first start.

```bash
# Start the database
docker compose up -d

# Stop the database
docker compose down

# Stop and delete all data
docker compose down -v
```

## API Endpoints

| Endpoint                      | Method           | Description                       |
| ----------------------------- | ---------------- | --------------------------------- |
| `/api/auth/register/`         | POST             | Register a new user               |
| `/api/auth/login/`            | POST             | Obtain JWT tokens                 |
| `/api/auth/logout/`           | POST             | Blacklist refresh token           |
| `/api/auth/token/refresh/`    | POST             | Refresh access token              |
| `/api/crops/categories/`      | GET, POST        | List / create categories          |
| `/api/crops/categories/{id}/` | GET, PUT, DELETE | Category detail / update / delete |
| `/api/crops/crops/`           | GET, POST        | List / create crops (filtered)    |
| `/api/crops/crops/{id}/`      | GET, PUT, DELETE | Crop detail / update / delete     |
| `/api/crops/crops/export/`    | GET              | Export crops to Excel             |

## Running Tests

```bash
pytest -v
```

## API Documentation

Start the server and visit: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
