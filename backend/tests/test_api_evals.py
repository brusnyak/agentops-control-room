import json
import uuid

VALID_TEMPLATE = {
    "name": "Dental recall", "channel": "voice_simulated",
    "goal_prompt": "book an appointment", "eval_rubric": "Pass if clear",
}
VALID_SCRIPT_JSON = json.dumps({"script": "Hi, checking in about your appointment."})
VALID_JUDGE_JSON = json.dumps({"llm_score": 90, "passed": True, "failure_tags": [], "notes": "Good."})


def _make_run(client, mock_llm):
    template = client.post("/workflow-templates", json=VALID_TEMPLATE).json()
    campaign = client.post("/campaigns", json={"workflow_template_id": template["id"], "name": "C"}).json()
    contact = client.post("/contacts", json={"name": "Jane"}).json()
    mock_llm.responses.append(VALID_SCRIPT_JSON)
    run = client.post("/runs", json={"campaign_id": campaign["id"], "contact_id": contact["id"]}).json()
    return run


def test_create_evaluation(client, mock_llm):
    run = _make_run(client, mock_llm)
    mock_llm.responses.append(VALID_JUDGE_JSON)

    response = client.post(f"/evals/{run['id']}")

    assert response.status_code == 201
    body = response.json()
    assert body["llm_score"] == 90
    assert body["rule_score"] == 1.0


def test_evaluation_not_found_run(client, mock_llm):
    response = client.post(f"/evals/{uuid.uuid4()}")
    assert response.status_code == 404


def test_list_evaluations(client, mock_llm):
    run = _make_run(client, mock_llm)
    mock_llm.responses.append(VALID_JUDGE_JSON)
    client.post(f"/evals/{run['id']}")

    response = client.get(f"/evals/{run['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 1
