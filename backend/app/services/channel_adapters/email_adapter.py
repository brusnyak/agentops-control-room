"""Real email adapter via Resend (free tier: 100 emails/day, 3,000/month, no card required).

This is the one genuinely-real channel in the MVP — everything else is simulated. Real
external side-effect, real API call, real failure modes to handle.

Safety note: the verified sending domain on the free tier is shared with Recareo's real
outreach. Faker-seeded demo contacts have addresses at reserved-for-example domains
(example.com/.org/.net, RFC 2606) that don't exist and would hard-bounce, which risks the
shared domain's sending reputation. Refusing those before they ever hit Resend costs nothing
and prevents an easy accidental self-inflicted deliverability problem.
"""

from __future__ import annotations

import httpx

from app.config import settings
from app.services.channel_adapters.base import ChannelAdapter, ChannelResult

RESEND_URL = "https://api.resend.com/emails"

# RFC 2606 reserved domains — Faker and most test fixtures generate addresses here. These will
# always bounce; never attempt a real send to them regardless of what triggered the run.
_RESERVED_EXAMPLE_DOMAINS = {"example.com", "example.org", "example.net", "example.edu"}


class EmailAdapter(ChannelAdapter):
    provider_name = "resend"

    def send(self, *, contact_name: str, contact_email: str | None, contact_phone: str | None, script: str) -> ChannelResult:
        if not contact_email:
            return ChannelResult(
                success=False, provider=self.provider_name, outcome="failed",
                response_content="", error="Contact has no email address",
            )
        if contact_email.strip().lower().split("@")[-1] in _RESERVED_EXAMPLE_DOMAINS:
            return ChannelResult(
                success=False, provider=self.provider_name, outcome="failed",
                response_content="",
                error=(
                    f"Refusing to send to '{contact_email}' — reserved example domain, would "
                    "hard-bounce and risk the shared sending domain's reputation. Use a real "
                    "address (e.g. your own) for email-channel demo runs."
                ),
            )
        if not settings.resend_api_key:
            return ChannelResult(
                success=False, provider=self.provider_name, outcome="failed",
                response_content="", error="RESEND_API_KEY is not configured",
            )

        try:
            response = httpx.post(
                RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": settings.resend_from_email,
                    "to": [contact_email],
                    "subject": f"Following up, {contact_name}",
                    "text": script,
                },
                timeout=30,
            )
        except httpx.HTTPError as exc:
            return ChannelResult(
                success=False, provider=self.provider_name, outcome="failed",
                response_content="", error=str(exc),
            )

        if response.status_code >= 400:
            return ChannelResult(
                success=False, provider=self.provider_name, outcome="failed",
                response_content="", error=f"Resend {response.status_code}: {response.text[:200]}",
            )

        return ChannelResult(
            success=True, provider=self.provider_name, outcome="sent",
            response_content=f"Email sent to {contact_email} (id: {response.json().get('id', 'n/a')})",
        )
