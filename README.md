# LearnPath AI Study Assistant

An AI-powered study assistant that enables students to ask curriculum-grounded questions while providing administrators with tools to manage users, curriculum imports, and system activity.

The project demonstrates production-oriented backend architecture including asynchronous processing, event-driven workflows, background jobs, and a Retrieval-Augmented Generation (RAG) pipeline.

---

# Features

## Student

- Secure JWT authentication
- Create multiple chat sessions
- Curriculum-grounded AI responses
- Persistent conversation history
- Asynchronous AI processing
- Automatic retry for transient AI failures

## Administrator

- Manage users
- Suspend/unsuspend accounts
- Upload curriculum
- Background curriculum processing
- Duplicate upload detection
- Import history
- Audit logging

## Platform

- Event-driven architecture
- Transactional Outbox Pattern
- Celery background workers
- Independent Analytics and Compliance consumers
- Redis-backed task queue
- PostgreSQL persistence
- Dockerized development environment

---

# Technology Stack

| Layer | Technology |
|---------|------------|
| Frontend | React, TypeScript, Material UI, Vite |
| Backend | FastAPI, Python |
| Database | PostgreSQL + pgvector |
| Queue | Redis |
| Background Jobs | Celery |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT |
| Testing | Pytest |
| Containerization | Docker Compose |

---

# Architecture

```
                        React + TypeScript
                               |
                               |
                         FastAPI REST API
                               |
      ------------------------------------------------
      |                     |                        |
 Authentication        Curriculum Import         Chat API
      |                     |                        |
      |                     |                        |
 PostgreSQL <--------- Import Jobs ---------- Chat Sessions
      |
      |
 Transactional Outbox
      |
      |
 Celery Beat
      |
      |
 Publish Pending Events
      |
      |
 Celery Worker
      |
      |-------------------------------|
      |                               |
Chat Processing                  Import Processing
      |
      |
Chat Completed Event
      |
      |
-------------------------------
|                             |
Analytics Consumer      Compliance Consumer
```

---

# Repository Structure

```
backend/
    app/
    alembic/
    tests/

frontend/
    src/

docs/
    adr/

sample-data/
```

---

# Prerequisites

- Python 3.11+
- Node.js 22+
- Docker Desktop

---

# Running the Project

Clone the repository.

Copy the environment variables.

```bash
cp .env.example .env
```

Start infrastructure.

```bash
docker compose up -d
```

---

## Backend

```bash
cd backend

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Swagger

```
http://localhost:8000/docs
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Application

```
http://localhost:5173
```

---

# Docker Services

The application consists of five containers.

| Service | Purpose |
|----------|----------|
| postgres | PostgreSQL database |
| redis | Redis task broker |
| api | FastAPI application |
| worker | Celery worker |
| beat | Celery scheduler |

Start everything.

```bash
docker compose up --build -d
```

---

# Creating the Initial Administrator

Public registration always creates student accounts.

Create the first administrator using:

```bash
cd backend

source .venv/bin/activate

python -m app.scripts.create_admin --email admin@example.com
```

You'll be prompted to securely enter the password.

---

# Running Tests

```bash
cd backend

source .venv/bin/activate

pytest -v
```

Current coverage includes:

- Authentication
- Registration
- Login
- Chat service
- Retrieval pipeline
- Curriculum search

---

# Reviewer Walkthrough

## 1. Start the application

```bash
docker compose up --build -d
```

---

## 2. Create an administrator

```bash
python -m app.scripts.create_admin --email admin@example.com
```

---

## 3. Login as Administrator

Open Swagger.

```
http://localhost:8000/docs
```

Authenticate.

---

## 4. Upload Sample Curriculum

Use:

```
sample-data/curriculum.jsonl
```

Wait a few seconds for the background import to complete.

---

## 5. Register a Student

Use the Register endpoint or the frontend.

---

## 6. Login as Student

Create a chat session.

---

## 7. Ask Questions

The uploaded curriculum contains answers for questions such as:

```
What is photosynthesis?

Explain Newton's first law.

Summarize the French Revolution.

What is the quadratic formula?

Explain the water cycle.
```

Responses should be grounded in the uploaded curriculum.

---

## 8. Verify Event Processing (Optional)

Each completed chat interaction produces an Outbox event.

That event is independently consumed by:

- Analytics Consumer
- Compliance Consumer

Verify using:

```sql
SELECT * FROM analytics_events;

SELECT * FROM compliance_events;

SELECT * FROM outbox_events;
```

---

# Key Design Decisions

## Asynchronous Chat Processing

Student messages are queued using Celery to prevent long-running AI requests from blocking HTTP requests.

---

## Transactional Outbox Pattern

Chat completion events are first written to an Outbox table within the same database transaction.

A background publisher reliably delivers these events to downstream consumers.

This prevents lost events if the application crashes between committing the database transaction and publishing the event.

---

## Event-Driven Consumers

Analytics and Compliance are implemented as completely independent consumers.

Each maintains its own persistence model and processes events idempotently.

---

## Curriculum Retrieval

Responses are grounded exclusively in uploaded curriculum.

The retrieval pipeline:

- Normalizes user questions
- Removes instructional stop words
- Uses PostgreSQL full-text search
- Ranks matching curriculum records
- Supplies context to the AI provider

---

# Future Improvements

Given additional time, I would implement:

- Streaming AI responses
- Semantic vector search with pgvector embeddings
- WebSocket chat updates
- Role-based permissions beyond Admin/Student
- Prometheus metrics
- OpenTelemetry tracing
- Kubernetes deployment
- CI/CD pipeline
- Integration tests
- Rate limiting
- Distributed tracing

---

# Screenshots

*(Add screenshots here before submission.)*

Suggested screenshots:

- Login page
- Student dashboard
- Chat conversation
- Admin dashboard
- Curriculum upload
- Swagger API

---

# Author

Adekunle Ademefun