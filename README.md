# AgentOps Control Room

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-7C3AED)](https://openrouter.ai/)
[![Resend](https://img.shields.io/badge/Email-Resend-000000)](https://resend.com/)
[![Docker](https://img.shields.io/badge/Runtime-Docker_Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Tests](https://img.shields.io/badge/Tests-pytest-0F766E)](https://docs.pytest.org/)

AgentOps Control Room is a full-stack AI operations project for running configurable outbound and ops workflows across email, voice, and SMS-style channels with measurable execution, evaluation, and observability.

Target roles: AI Automation Engineer, Applied AI Engineer, Agent Harness Engineer, Forward Deployed Engineer.

## Overview

This project is built around a practical pattern employers keep asking for: AI workflows connected to real systems, with evaluation loops and production-style reliability. Instead of being another chatbot demo, AgentOps Control Room models the operational layer around agents: contacts, campaign templates, workflow runs, message logs, tool-call logs, webhook ingestion, run evaluation, and observability.

The backend is implemented and verified end-to-end. The recruiter/ops dashboard frontend is planned but not started yet.

## Status

| Area | Status | Notes |
| --- | --- | --- |
| Contacts | Done | CRUD endpoints for managing workflow targets. |
| Workflow templates | Done | Configurable templates for follow-up, qualification, booking, and support triage. |
| Campaigns | Done | Campaign records and dashboard metrics. |
| Run engine | Done | Script generation, channel dispatch, transcript logging, tool-call logging, and outcome tracking. |
| Email adapter | Done | Real email channel through Resend. |
| Voice and SMS adapters | Simulated | Clearly labeled simulated adapters for MVP workflow coverage. |
| Evaluation | Done | Rule-based checks plus LLM-as-judge rubric per run. |
| Observability | Done | LLM call stats, latency, success rate, and purpose breakdown. |
| Webhook ingestion | Done | Inbound webhook endpoint for external events. |
| Frontend dashboard | Planned | Next.js/Tailwind/shadcn UI path exists but implementation is not started. |
| Webhook export | Planned | Import exists; result export is not implemented yet. |

## Features

| Feature | Details |
| --- | --- |
| Configurable workflows | Reusable workflow templates for common outbound and ops flows. |
| Campaign execution | Trigger a workflow run for a campaign/contact pair. |
| Channel abstraction | Email is real through Resend; voice and SMS are simulated adapters. |
| Run logging | Records messages, transcripts, tool calls, outcomes, and failure reasons. |
| Evaluation layer | Combines deterministic rule checks with LLM-judge scoring. |
| Dashboard data | Outcome counts, failure reasons, and latency metrics per campaign. |
| LLM observability | Tracks call count, latency, success rate, and model usage patterns. |
| Webhook ingestion | Accepts inbound events through `POST /webhooks/inbound`. |
| Test isolation | Uses a dedicated `_test` database for test runs. |

## System design

```mermaid
flowchart TB
    Operator([Operator]) --> API[FastAPI Control API]
    Dashboard[Future Ops Dashboard] --> API

    API --> Contacts[Contacts]
    API --> Templates[Workflow Templates]
    API --> Campaigns[Campaigns]
    API --> Runs[Run Engine]

    Runs --> Script[LLM Script Generation]
    Script --> OpenRouter[OpenRouter LLM]
    Runs --> Channels[Channel Adapters]
    Channels --> Email[Resend Email]
    Channels --> Simulated[Simulated Voice / SMS]

    Runs --> Eval[Rule + LLM Evaluation]
    Eval --> OpenRouter

    API --> Webhooks[Inbound Webhooks]
    API --> Observability[Observability API]

    Contacts --> DB[(PostgreSQL)]
    Templates --> DB
    Campaigns --> DB
    Runs --> DB
    Eval --> DB
    Webhooks --> DB
    Observability --> DB

    classDef actor fill:#DBEAFE,stroke:#2563EB,color:#0F172A,stroke-width:1px
    classDef client fill:#EDE9FE,stroke:#7C3AED,color:#0F172A,stroke-width:1px
    classDef backend fill:#DCFCE7,stroke:#16A34A,color:#0F172A,stroke-width:1px
    classDef ai fill:#FEF3C7,stroke:#D97706,color:#0F172A,stroke-width:1px
    classDef channel fill:#CCFBF1,stroke:#0F766E,color:#0F172A,stroke-width:1px
    classDef data fill:#FCE7F3,stroke:#DB2777,color:#0F172A,stroke-width:1px

    class Operator actor
    class Dashboard client
    class API,Contacts,Templates,Campaigns,Runs,Webhooks,Observability backend
    class Script,OpenRouter,Eval ai
    class Channels,Email,Simulated channel
    class DB data
```

### Runtime flow

| Step | Component | Responsibility |
| --- | --- | --- |
| 1 | Operator or API client | Creates contacts, templates, and campaigns. |
| 2 | Run engine | Starts a workflow run for a selected campaign/contact pair. |
| 3 | LLM script generation | Produces the message or workflow script through OpenRouter. |
| 4 | Channel adapter | Dispatches through real email or simulated voice/SMS adapters. |
| 5 | Logging layer | Stores messages, tool calls, transcripts, outcomes, latency, and failures. |
| 6 | Evaluation layer | Runs rule checks and LLM-as-judge scoring against each run. |
| 7 | Dashboard/observability | Reports outcomes, failures, campaign metrics, and LLM usage. |

## Tech stack

| Layer | Choice | Notes |
| --- | --- | --- |
| Backend | FastAPI, Uvicorn | Main API service. |
| Database | PostgreSQL 16 | Stores contacts, campaigns, workflow runs, messages, evaluations, and logs. |
| ORM and migrations | SQLAlchemy, Alembic | Database models and schema evolution. |
| Schemas | Pydantic | Request/response validation and typed configuration. |
| AI provider | OpenRouter | LLM script generation and LLM-as-judge evaluation. |
| Email | Resend | Real outbound email adapter. |
| Simulated channels | Voice and SMS adapters | MVP coverage without paid telephony/SMS dependencies. |
| Testing | pytest, Faker | Unit and API tests. |
| Local runtime | Docker Compose | Backend, frontend placeholder, and Postgres. |
| Planned frontend | Next.js, TypeScript, Tailwind, shadcn/ui | Dashboard UI path; not started yet. |

## API areas

| Area | Purpose |
| --- | --- |
| `/contacts` | Manage contact records. |
| `/workflow-templates` | Manage reusable workflow templates. |
| `/campaigns` | Manage campaigns and campaign-level reporting. |
| `/runs` | Trigger and inspect workflow runs. |
| `/evals` | Evaluate run quality and outcomes. |
| `/dashboard` | Fetch dashboard metrics such as outcomes, failures, and latency. |
| `/webhooks/inbound` | Ingest inbound external events. |
| `/observability/stats` | Inspect LLM usage, latency, and reliability metrics. |
| `/health` | Service health check. |

## Quick start

Requirements:

- Docker and Docker Compose
- `OPENROUTER_API_KEY` in `~/.secrets/acore.env`
- `RESEND_API_KEY` in `~/.secrets/acore.env` for real email dispatch

Generate the backend environment file:

```bash
./scripts/setup-env.sh
```

Start Postgres and the backend:

```bash
docker compose up -d postgres
docker compose build backend
docker compose up -d backend
```

Create the development schema and seed demo data:

```bash
docker compose run --rm backend python -m app.init_db
docker compose run --rm backend python -m seed.seed_data
```

Check the service health:

```bash
curl http://localhost:8001/health
```

List campaigns and trigger a run:

```bash
curl http://localhost:8001/campaigns
curl -X POST http://localhost:8001/runs \
  -H "Content-Type: application/json" \
  -d '{"campaign_id": "<id>", "contact_id": "<id>"}'
```

## Testing

Create a dedicated test database and run tests against it:

```bash
docker exec agentops-control-room-postgres-1 psql -U postgres -c "CREATE DATABASE agentops_test;" 2>/dev/null || true
docker compose run --rm \
  -e DATABASE_URL="postgresql+psycopg://postgres:postgres@postgres:5432/agentops_test" \
  -e APP_ENV=test \
  backend pytest -v
```

Do not run tests against the default development database. The test suite is designed to use a dedicated `_test` database.

## Port layout

Ports are offset from `ai-recruitment-copilot` so both portfolio projects can run side by side.

| Service | AgentOps port | Recruitment Copilot equivalent |
| --- | --- | --- |
| Backend | `8001` | `8000` |
| Frontend | `3001` | `3000` |
| Postgres | `5433` | `5432` |

## Design notes

### Synchronous run engine

Workflow runs currently execute synchronously. The API call blocks until the LLM and channel adapter finish, usually around 5–30 seconds depending on free-tier model latency.

A production version would move run execution to a queue. This is a deliberate MVP tradeoff to keep the control loop simple and inspectable.

### Real and simulated channels

Email uses a real Resend adapter. Voice and SMS are simulated so the workflow, logging, evaluation, and observability layers can be demonstrated without paid telephony dependencies.

## Project structure

```text
agentops-control-room/
├── backend/             # FastAPI app, routers, services, tests, seed data
├── frontend/            # Planned Next.js dashboard
├── docs/                # Research and supporting project notes
├── scripts/             # Environment setup helpers
├── docker-compose.yml   # Local Postgres, backend, and frontend runtime
└── README.md
```

## README style direction

This repository follows the shared portfolio README structure:

- Short product description at the top.
- Technology labels for fast scanning.
- Status, feature, API, and runtime-flow tables.
- Coloured system design diagram when architecture is useful.
- Practical setup, testing, design notes, and project structure.

## Roadmap

- Build the recruiter/ops dashboard UI.
- Add webhook export for run results.
- Add screenshots and a short demo video.
- Add cost and safety notes.
- Move synchronous run execution to a background queue for production-style scaling.
