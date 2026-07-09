from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import campaigns, contacts, dashboard, evals, health, observability, runs, webhooks, workflow_templates

app = FastAPI(title="AgentOps Control Room", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(contacts.router)
app.include_router(workflow_templates.router)
app.include_router(campaigns.router)
app.include_router(runs.router)
app.include_router(evals.router)
app.include_router(dashboard.router)
app.include_router(webhooks.router)
app.include_router(observability.router)
