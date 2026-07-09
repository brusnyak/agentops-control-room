# AgentOps Control Room

A full-stack app for running configurable AI outbound/ops workflows (voice, SMS, email) with full observability: every run, message, tool call, and evaluation is logged and measurable.

**Target roles:** AI Automation Engineer / Applied AI Engineer / Agent Harness Engineer / Forward Deployed Engineer
**Reference postings:** Huzzle (AI Automation Engineer), Duvo (Forward Deployed Engineer), Action1 (Applied AI Engineer), Viktor (Agent Harness Engineer), JUPUS (Voice Agent Evaluation) — see `docs/research.md`

## Why this project

Market research across 16 real postings (Reedsy, n8n, Viktor, Duvo, Action1, JUPUS, Huzzle, and others) shows a consistent pattern: employers want engineers who can ship AI workflows connected to real systems, with evaluation loops and production reliability — not another chatbot demo. This project is built to close that specific gap.

## Status

Backend done: contacts, configurable workflow templates, campaigns, a run engine (script generation → channel dispatch → transcript/tool-call logging), rule + LLM-judge evaluation, a campaign dashboard, LLM observability, and webhook ingestion. 36 passing tests, live-verified against a real OpenRouter model end to end (script generation → simulated channel → evaluation, ~6s per run). Frontend not started yet.

## Core features

- [x] Contacts CRUD
- [x] Configurable workflow templates (follow-up, qualification, booking, support triage) across email/voice/SMS
- [x] Run engine: trigger a workflow run per contact, log every message/tool-call/outcome
- [x] One real channel adapter (email via Resend) + two clearly-labeled simulated adapters (voice, SMS)
- [x] Evaluation: rule-based checks + LLM-as-judge rubric per run
- [x] Dashboard: outcome counts, failure reasons, latency per campaign
- [x] LLM observability (`GET /observability/stats`)
- [x] Inbound webhook ingestion (`POST /webhooks/inbound`)
- [ ] Recruiter/ops dashboard UI (frontend)
- [ ] Webhook export of results (currently import-only)

## Stack

- Frontend: Next.js, TypeScript, Tailwind, shadcn/ui (not started)
- Backend: FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- AI: OpenRouter (free-tier models) — LLM client, retry/observability, and eval patterns ported directly from [ai-recruitment-copilot](https://github.com/brusnyak/ai-recruitment-copilot)
- Email: Resend (free tier: 100/day, 3,000/month, no card required)
- Infra: Docker Compose (dedicated `_test` DB, same lesson learned from Project 1), GitHub Actions CI

## Acceptance criteria

- [ ] Clean README with screenshots
- [x] Working local setup with docker compose
- [x] Seed dataset with mock contacts/campaigns (`docker compose run --rm backend python -m seed.seed_data`)
- [x] Meaningful test suite (36 passing: unit + API)
- [ ] Demo video or Loom
- [ ] Architecture diagram
- [ ] Cost/safety notes

## Setup

Requires Docker and `~/.secrets/acore.env` with `OPENROUTER_API_KEY` (shared with ai-recruitment-copilot) and `RESEND_API_KEY` (free at [resend.com/signup](https://resend.com/signup) — needed only for the real email channel; everything else works without it).

```bash
# 1. Generate backend/.env from your central secrets + this project's defaults
./scripts/setup-env.sh

# 2. Start Postgres and the backend
docker compose up -d postgres
docker compose build backend
docker compose up -d backend

# 3. Create the dev schema and seed demo data
docker compose run --rm backend python -m app.init_db
docker compose run --rm backend python -m seed.seed_data

# 4. Check it's alive
curl http://localhost:8001/health

# 5. Try it — list a campaign, then trigger a run
curl http://localhost:8001/campaigns
curl -X POST http://localhost:8001/runs -H "Content-Type: application/json" \
  -d '{"campaign_id": "<id>", "contact_id": "<id>"}'

# 6. Run tests — against a DEDICATED test database, never the dev one
docker exec agentops-control-room-postgres-1 psql -U postgres -c "CREATE DATABASE agentops_test;" 2>/dev/null || true
docker compose run --rm \
  -e DATABASE_URL="postgresql+psycopg://postgres:postgres@postgres:5432/agentops_test" \
  -e APP_ENV=test \
  backend pytest -v
```

**Ports are offset from ai-recruitment-copilot** (8001/3001/5433 instead of 8000/3000/5432) so both portfolio projects can run side by side without conflicts.

**Note on the run engine**: runs execute synchronously (the API call blocks until the LLM + channel adapter finish, ~5-30s depending on the free-tier model's latency). A production system would queue this — documented tradeoff for MVP simplicity, not an oversight.
