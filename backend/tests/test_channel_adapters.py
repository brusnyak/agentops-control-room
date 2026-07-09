from app.services.channel_adapters.email_adapter import EmailAdapter
from app.services.channel_adapters.simulated_adapter import OUTCOMES, SimulatedSmsAdapter, SimulatedVoiceAdapter

VALID_OUTCOMES = {o for o, _ in OUTCOMES}


def test_email_adapter_fails_without_contact_email():
    adapter = EmailAdapter()
    result = adapter.send(contact_name="Jane", contact_email=None, contact_phone=None, script="hi")

    assert result.success is False
    assert "email" in result.error.lower()


def test_email_adapter_fails_without_api_key(monkeypatch):
    monkeypatch.setattr("app.services.channel_adapters.email_adapter.settings.resend_api_key", "")
    adapter = EmailAdapter()
    result = adapter.send(contact_name="Jane", contact_email="jane@realcompany.com", contact_phone=None, script="hi")

    assert result.success is False
    assert "RESEND_API_KEY" in result.error


def test_email_adapter_refuses_reserved_example_domain():
    adapter = EmailAdapter()
    result = adapter.send(contact_name="Jane", contact_email="jane@example.com", contact_phone=None, script="hi")

    assert result.success is False
    assert "reserved example domain" in result.error


def test_email_adapter_refuses_reserved_example_domain_case_insensitive():
    adapter = EmailAdapter()
    result = adapter.send(contact_name="Jane", contact_email="Jane@EXAMPLE.ORG", contact_phone=None, script="hi")

    assert result.success is False
    assert "reserved example domain" in result.error


def test_simulated_voice_adapter_always_succeeds_with_valid_outcome():
    adapter = SimulatedVoiceAdapter()
    for _ in range(20):
        result = adapter.send(contact_name="Jane", contact_email=None, contact_phone="+1", script="hi")
        assert result.success is True
        assert result.outcome in VALID_OUTCOMES
        assert result.response_content.startswith("[SIMULATED]")


def test_simulated_sms_adapter_always_succeeds_with_valid_outcome():
    adapter = SimulatedSmsAdapter()
    for _ in range(20):
        result = adapter.send(contact_name="Jane", contact_email=None, contact_phone="+1", script="hi")
        assert result.success is True
        assert result.outcome in VALID_OUTCOMES
