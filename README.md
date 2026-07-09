# AgentOps Control Room

A full-stack app for running configurable AI outbound/ops workflows (voice, SMS, email) with full observability: every run, message, tool call, and evaluation is logged and measurable.

**Target roles:** AI Automation Engineer / Applied AI Engineer / Agent Harness Engineer / Forward Deployed Engineer
**Reference postings:** Huzzle (AI Automation Engineer), Duvo (Forward Deployed Engineer), Action1 (Applied AI Engineer), Viktor (Agent Harness Engineer), JUPUS (Voice Agent Evaluation) — see `docs/research.md`

## Why this project

Market research across 16 real postings (Reedsy, n8n, Viktor, Duvo, Action1, JUPUS, Huzzle, and others) shows a consistent pattern: employers want engineers who can ship AI workflows connected to real systems, with evaluation loops and production reliability — not another chatbot demo. This project is built to close that specific gap.

## Status

Scaffolding. Not yet functional.

## Core features (planned)

- Import contacts/leads (CSV)
- Configurable workflow templates (follow-up, qualification, booking, support triage) across voice/SMS/email
- Run engine: trigger a workflow run per contact, log every message/tool call/outcome
- One real channel adapter (email) + one clearly-labeled simulated adapter (voice/SMS)
- Evaluation: rule-based checks + LLM-as-judge rubric per run
- Dashboard: outcome counts, failure reasons, latency, run timeline
- Webhook export of results

## Stack

- Frontend: Next.js, TypeScript, Tailwind, shadcn/ui
- Backend: FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- AI: OpenRouter (free-tier models) — reusing the LLM client, retry/observability, and eval patterns proven in [ai-recruitment-copilot](https://github.com/brusnyak/ai-recruitment-copilot)
- Email: free-tier provider (TBD: Resend or Brevo)
- Infra: Docker Compose, GitHub Actions CI

## Acceptance criteria

- [ ] Clean README with screenshots
- [ ] Working local setup with docker compose
- [ ] Seed dataset with mock contacts/campaigns
- [ ] Meaningful test suite (unit + API)
- [ ] Demo video or Loom
- [ ] Architecture diagram
- [ ] Cost/safety notes

## Setup

TBD once backend skeleton exists.
