from app.schemas.script import ScriptParsed
from app.services.llm_client import LLMProvider
from app.services.parsing import ParsedResult, parse_structured

SYSTEM_PROMPT = (
    "You write short, natural outreach messages (email/call opener/SMS) for a business workflow. "
    "Given the workflow's goal and a contact's name, write ONE message that pursues that goal "
    "directly and briefly — no filler, no over-explaining. Respond with ONLY a single JSON "
    "object with key: script (string, the message text)."
)


def generate_script(llm: LLMProvider, *, goal_prompt: str, contact_name: str, channel: str) -> ParsedResult:
    user_prompt = (
        f"Workflow goal: {goal_prompt}\n"
        f"Channel: {channel}\n"
        f"Contact name: {contact_name}\n\n"
        f"Write the outreach message now."
    )
    result = parse_structured(llm, SYSTEM_PROMPT, user_prompt, ScriptParsed)
    assert isinstance(result.value, ScriptParsed)
    return result
