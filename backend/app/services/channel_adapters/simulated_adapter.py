"""Simulated voice/SMS adapter — no real telephony provider wired up.

Honest by design: real production voice/SMS needs a provider (Retell, Twilio, LiveKit) with
per-minute/per-message cost. For a portfolio demo, faking the outcome distribution while being
explicit in the UI/API that it's simulated is the correct tradeoff — see docs/architecture.md.
Clearly labeled, never presented as a real call/text.
"""

from __future__ import annotations

import random

from app.services.channel_adapters.base import ChannelAdapter, ChannelResult

OUTCOMES = [
    ("booked", "Contact agreed to the proposed time and confirmed booking."),
    ("follow_up", "Contact asked to be contacted again next week."),
    ("no_answer", "No response after simulated attempt."),
    ("declined", "Contact declined the offer."),
]
OUTCOME_WEIGHTS = [0.35, 0.25, 0.25, 0.15]


class SimulatedVoiceAdapter(ChannelAdapter):
    provider_name = "simulated_voice"

    def send(self, *, contact_name: str, contact_email: str | None, contact_phone: str | None, script: str) -> ChannelResult:
        outcome, response = random.choices(OUTCOMES, weights=OUTCOME_WEIGHTS, k=1)[0]
        return ChannelResult(
            success=True,
            provider=self.provider_name,
            outcome=outcome,
            response_content=f"[SIMULATED] {response}",
        )


class SimulatedSmsAdapter(ChannelAdapter):
    provider_name = "simulated_sms"

    def send(self, *, contact_name: str, contact_email: str | None, contact_phone: str | None, script: str) -> ChannelResult:
        outcome, response = random.choices(OUTCOMES, weights=OUTCOME_WEIGHTS, k=1)[0]
        return ChannelResult(
            success=True,
            provider=self.provider_name,
            outcome=outcome,
            response_content=f"[SIMULATED] {response}",
        )
