import json
import uuid

VALID_TEMPLATE = {
    "name": "Dental recall", "channel": "voice_simulated",
    "goal_prompt": "book an appointment", "eval_rubric": "Pass if clear",
}
VALID_SCRIPT_JSON = json.dumps({"script": "Hi, checking in about your appointment."})


def _setup_campaign_and_contact(client):
    template = client.post("/workflow-templates", json=VALID_TEMPLATE).json()
    campaign = client.post("/campaigns", json={"workflow_template_id": template["id"], "name": "C"}).json()
    contact = client.post("/contacts", json={"name": "Jane Doe", "phone": "+1555"}).json()
    return campaign, contact


def test_create_run_simulated_channel_completes(client, mock_llm):
    campaign, contact = _setup_campaign_and_contact(client)
    mock_llm.responses.append(VALID_SCRIPT_JSON)

    response = client.post("/runs", json={"campaign_id": campaign["id"], "contact_id": contact["id"]})

    assert response.status_code == 201
    body = response.json()
    assert body["state"] == "completed"
    assert body["outcome"] is not None


def test_get_run_detail_includes_messages(client, mock_llm):
    campaign, contact = _setup_campaign_and_contact(client)
    mock_llm.responses.append(VALID_SCRIPT_JSON)
    run = client.post("/runs", json={"campaign_id": campaign["id"], "contact_id": contact["id"]}).json()

    response = client.get(f"/runs/{run['id']}")

    assert response.status_code == 200
    detail = response.json()
    assert len(detail["messages"]) >= 1
    assert len(detail["tool_calls"]) == 1


def test_create_run_campaign_not_found(client, mock_llm):
    contact = client.post("/contacts", json={"name": "Jane"}).json()
    response = client.post("/runs", json={"campaign_id": str(uuid.uuid4()), "contact_id": contact["id"]})
    assert response.status_code == 404


def test_list_runs_filtered_by_campaign(client, mock_llm):
    campaign, contact = _setup_campaign_and_contact(client)
    mock_llm.responses.append(VALID_SCRIPT_JSON)
    client.post("/runs", json={"campaign_id": campaign["id"], "contact_id": contact["id"]})

    response = client.get(f"/runs?campaign_id={campaign['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 1
