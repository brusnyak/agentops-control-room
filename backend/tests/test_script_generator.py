import json

import pytest

from app.services.llm_client import MockLLMProvider
from app.services.parsing import ParsingFailedError
from app.services.script_generator import generate_script

VALID_JSON = json.dumps({"script": "Hi Jane, following up on your demo request — got 15 min this week?"})


def test_generate_script_valid_first_try():
    llm = MockLLMProvider(responses=[VALID_JSON])
    result = generate_script(llm, goal_prompt="Follow up on a lead", contact_name="Jane", channel="email")

    assert "Jane" in result.value.script or "following up" in result.value.script.lower()
    assert len(llm.calls) == 1


def test_generate_script_retries_on_invalid_json():
    llm = MockLLMProvider(responses=["not json", VALID_JSON])
    result = generate_script(llm, goal_prompt="Follow up", contact_name="Jane", channel="email")

    assert result.value.script
    assert len(llm.calls) == 2


def test_generate_script_gives_up_after_max_attempts():
    llm = MockLLMProvider(responses=["nope", "nope", "nope"])
    with pytest.raises(ParsingFailedError):
        generate_script(llm, goal_prompt="Follow up", contact_name="Jane", channel="email")
