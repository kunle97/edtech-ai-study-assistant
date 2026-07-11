# LearnPath AI Study Assistant

LearnPath is an AI-powered study assistant built for the Pearson Senior Software Engineer take-home assignment.

The application allows students to interact with an AI tutor through persistent chat sessions while giving administrators tools to manage users and maintain an immutable audit trail. AI requests are processed asynchronously to provide fast API responses and reliable background execution.

---

# Technology Stack

## Frontend

- React
- TypeScript
- Vite

## Backend

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery

## Infrastructure

- Docker Compose
- pgvector (planned for RAG)

---

# Architecture

```text
                    React + TypeScript
                            │
                            ▼
                  FastAPI REST API
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
 PostgreSQL                                Redis Queue
(users, chats, audit)                           │
        ▲                                       ▼
        └──────────── Celery Worker ────────────┘
                            │
                            ▼
                   AI Provider Abstraction
                     (Mock Provider Today)
```

### Responsibilities

**FastAPI**

- Authentication
- Authorization
- REST API
- Validation
- Request handling

**PostgreSQL**

- Users
- Chat sessions
- Chat messages
- Audit logs

**Redis**

- Celery broker
- Background job queue

**Celery**

- AI processing
- Retries
- Background execution

**AI Provider**

Currently uses a mock implementation to keep the project self-contained.

The provider interface can later be replaced with:

- OpenAI
- Azure OpenAI
- Anthropic
- Gemini
- Local LLMs

without changing the application architecture.

---

# Features

## Authentication

- JWT authentication
- Password hashing
- Student registration
- Login
- Current user endpoint

## Administration

- Administrator accounts
- Suspend users
- Reinstate users
- List users
- Immutable audit logs

## Chat

- Persistent chat sessions
- Persistent messages
- Conversation history
- Asynchronous AI processing
- Automatic retries

## Reliability

- Background AI processing
- Retry handling
- Message status tracking
- Idempotent worker execution

---

# Design Decisions

## FastAPI

FastAPI was selected because it provides:

- excellent performance
- automatic OpenAPI documentation
- strong typing
- simple dependency injection

---

## PostgreSQL

PostgreSQL stores:

- users
- conversations
- audit logs

A relational database is appropriate because these entities have strong
relationships and transactional consistency requirements.

---

## Redis

Redis is used exclusively as the Celery broker.

Using Redis allows AI requests to execute outside the request lifecycle.

---

## Celery

AI requests can take several seconds.

Instead of blocking the HTTP request:

1. the student message is stored
2. the API immediately returns
3. Celery processes the request
4. the assistant response is persisted

Benefits:

- better responsiveness
- retries
- scalability
- fault tolerance

---

## Audit Logs

Administrative actions create immutable audit records.

Audit records are append-only and are never updated or deleted.

---

## AI Provider Abstraction

The application never directly depends on a specific LLM.

Instead it depends on an interface.

Current implementation:

- MockAIProvider

Future implementations can include:

- OpenAI
- Azure OpenAI
- Anthropic

without modifying business logic.

---

# Project Structure

```
backend/
    app/
        admin/
        ai/
        audit/
        auth/
        chat/
        worker/
    alembic/

frontend/
    src/

docs/
    adr/

sample-data/

docker-compose.yml
```

---

# Prerequisites

- Docker Desktop
- Python 3.12+
- Node.js 22+

---

# Quick Start (Recommended)

Clone the repository

```bash
git clone <repository-url>
cd edtech-ai-study-assistant
```

Copy environment variables

```bash
cp .env.example .env
```

Start everything

```bash
docker compose up --build
```

This starts:

- PostgreSQL
- Redis
- FastAPI
- Celery Worker

Swagger UI

```
http://localhost:8000/docs
```

---

# Local Development

## Backend

```bash
cd backend

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

alembic upgrade head

python -m uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Create an Administrator

Student registration is public.

Administrator accounts must be created manually.

```bash
cd backend

source .venv/bin/activate

python -m app.scripts.create_admin \
    --email admin@example.com
```

The password is entered securely using an interactive prompt.

---

# Running Tests

Start PostgreSQL

```bash
docker compose up -d postgres
```

Run tests

```bash
cd backend

source .venv/bin/activate

pytest -v
```

Each test runs inside a transaction which is rolled back after completion.

---

# API Documentation

Swagger UI

```
http://localhost:8000/docs
```

OpenAPI JSON

```
http://localhost:8000/openapi.json
```

---

# Useful Commands

Start containers

```bash
docker compose up --build
```

Stop containers

```bash
docker compose down
```

View logs

```bash
docker compose logs api

docker compose logs worker
```

Run backend

```bash
python -m uvicorn app.main:app --reload
```

Run Celery

```bash
python -m celery \
-A app.worker.celery_app:celery_app \
worker \
--loglevel=info
```

Run tests

```bash
pytest -v
```

---

# Current Implementation

✅ JWT Authentication

✅ Student Registration

✅ Login

✅ Role-Based Authorization

✅ Administrator Accounts

✅ User Suspension

✅ User Reinstatement

✅ Immutable Audit Logs

✅ Persistent Chat Sessions

✅ Persistent Chat Messages

✅ Asynchronous AI Processing

✅ Celery Worker

✅ Retry Logic

⬜ Curriculum Import

⬜ Vector Embeddings

⬜ Retrieval Augmented Generation (RAG)

⬜ Streaming AI Responses

⬜ React Study Interface

---

# Future Improvements

- pgvector semantic search
- curriculum ingestion pipeline
- Retrieval-Augmented Generation
- streaming responses using Server-Sent Events
- OpenTelemetry tracing
- rate limiting
- distributed worker autoscaling
- AI conversation summarization
- conversation search
- instructor analytics

---

# Why This Architecture?

The primary design goal was separation of concerns.

- FastAPI is responsible for HTTP.
- PostgreSQL is responsible for persistence.
- Redis transports work.
- Celery executes background jobs.
- AI providers generate responses.

Because these responsibilities are isolated, individual components can evolve independently without affecting the rest of the system.

This keeps the application maintainable, testable, and production-ready.