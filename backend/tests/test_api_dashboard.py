import json

VALID_TEMPLATE = {
    "name": "Dental recall", "channel": "voice_simulated",
    "goal_prompt": "book an appointment", "eval_rubric": "Pass if clear",
}
VALID_SCRIPT_JSON = json.dumps({"script": "Hi, checking in."})


def test_dashboard_aggregates_runs(client, mock_llm):
    template = client.post("/workflow-templates", json=VALID_TEMPLATE).json()
    campaign = client.post("/campaigns", json={"workflow_template_id": template["id"], "name": "C"}).json()
    contact = client.post("/contacts", json={"name": "Jane"}).json()

    mock_llm.responses.append(VALID_SCRIPT_JSON)
    client.post("/runs", json={"campaign_id": campaign["id"], "contact_id": contact["id"]})

    response = client.get(f"/dashboard/{campaign['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["total_runs"] == 1
    assert body["completed"] == 1
