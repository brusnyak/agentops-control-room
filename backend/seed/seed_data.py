"""Seed the database with demo workflow templates, campaigns, and fake contacts.
Run with: python -m seed.seed_data
"""

from __future__ import annotations

from faker import Faker

from app.db import SessionLocal
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.workflow_template import WorkflowTemplate

fake = Faker()

TEMPLATES = [
    {
        "name": "Lead follow-up (email)",
        "channel": "email",
        "goal_prompt": (
            "Follow up with a lead who requested a demo but went quiet. Politely check in, "
            "offer to answer questions, and propose a 15-minute call this week."
        ),
        "eval_rubric": (
            "Pass if the message is brief (under 100 words), proposes a concrete next step "
            "(a call/time), and doesn't sound pushy or generic."
        ),
    },
    {
        "name": "Dental recall (voice, simulated)",
        "channel": "voice_simulated",
        "goal_prompt": (
            "Call a dental patient who is overdue for a checkup. Remind them it's been a while, "
            "mention any current availability, and try to book an appointment."
        ),
        "eval_rubric": (
            "Pass if the message clearly states the purpose (overdue checkup), is warm and "
            "professional, and asks a direct question to move toward booking."
        ),
    },
    {
        "name": "Support triage (SMS, simulated)",
        "channel": "sms_simulated",
        "goal_prompt": (
            "A customer reported an issue via a support ticket. Send a short SMS acknowledging "
            "it, giving a rough timeline, and asking one clarifying question if needed."
        ),
        "eval_rubric": (
            "Pass if the message is under 320 characters, acknowledges the issue specifically, "
            "and doesn't overpromise a resolution time."
        ),
    },
]


def run(num_contacts: int = 12) -> None:
    db = SessionLocal()
    try:
        templates = []
        for t in TEMPLATES:
            template = WorkflowTemplate(**t)
            db.add(template)
            templates.append(template)
        db.flush()

        for template in templates:
            db.add(Campaign(workflow_template_id=template.id, name=f"{template.name} — demo campaign", status="active"))

        for _ in range(num_contacts):
            db.add(
                Contact(
                    name=fake.name(),
                    phone=fake.phone_number(),
                    email=fake.email(),
                    meta={"source": "seed"},
                )
            )

        db.commit()
        print(f"Seeded {len(templates)} workflow templates, {len(templates)} campaigns, {num_contacts} contacts.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
