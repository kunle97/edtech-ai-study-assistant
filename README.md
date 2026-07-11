# LearnPath AI Study Assistant

LearnPath is an AI-powered study assistant that allows students to interact
with a curriculum-grounded tutor and gives administrators tools for managing
users, curriculum imports, chat activity, and audit history.

## Technology Stack

- React and TypeScript
- Vite
- FastAPI and Python
- PostgreSQL with pgvector
- Redis
- Celery
- Docker Compose

## Project Structure

```text
backend/       FastAPI application and background workers
frontend/      React and TypeScript application
docs/adr/      Architecture decision records
sample-data/   Example curriculum import files
```

## Prerequisites
 - Python 3.11 or newer
 - Node.js 22
 - Docker and Docker Compose

## Quick Start

```bash
cp .env.example .env
docker compose up -d

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
nvm use
npm install
npm run dev
```

Backend API:
http://localhost:8000/docs

Frontend:
http://localhost:5173

## Create an Administrator

Public registration always creates student accounts. Create the initial
administrator with the backend command:

```bash
cd backend
source .venv/bin/activate
python -m app.scripts.create_admin --email admin@example.com
```

The password is entered securely through an interactive prompt.

## Run Backend Tests

PostgreSQL must be running:

```bash
docker compose up -d postgres

cd backend
source .venv/bin/activate
pytest -v
```

Each API test runs inside a database transaction that is rolled back after
the test.