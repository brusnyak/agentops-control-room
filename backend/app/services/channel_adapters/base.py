from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChannelResult:
    success: bool
    provider: str
    outcome: str  # e.g. "sent", "booked", "no_answer", "failed"
    response_content: str  # what the "other side" said/did, for the transcript
    error: str | None = None


class ChannelAdapter(ABC):
    provider_name: str = "unknown"

    @abstractmethod
    def send(self, *, contact_name: str, contact_email: str | None, contact_phone: str | None, script: str) -> ChannelResult:
        ...
