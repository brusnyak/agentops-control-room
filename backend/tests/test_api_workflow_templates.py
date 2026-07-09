import json
import uuid

VALID_TEMPLATE = {
    "name": "Lead follow-up",
    "channel": "email",
    "goal_prompt": "Follow up on a demo request",
    "eval_rubric": "Pass if brief and proposes a next step",
}
VALID_SCRIPT_JSON = json.dumps({"script": "Hi, checking in."})
VALID_JUDGE_JSON = json.dumps({"llm_score": 80, "passed": True, "failure_tags": [], "notes": "ok"})


def test_create_template(client, mock_llm):
    response = client.post("/workflow-templates", json=VALID_TEMPLATE)
    assert response.status_code == 201
    assert response.json()["channel"] == "email"
    assert response.json()["version"] == 1


def test_create_template_with_explicit_version(client, mock_llm):
    payload = {**VALID_TEMPLATE, "version": 2}
    response = client.post("/workflow-templates", json=payload)
    assert response.status_code == 201
    assert response.json()["version"] == 2


def test_create_template_rejects_invalid_channel(client, mock_llm):
    payload = {**VALID_TEMPLATE, "channel": "carrier_pigeon"}
    response = client.post("/workflow-templates", json=payload)
    assert response.status_code == 422


def test_list_templates(client, mock_llm):
    client.post("/workflow-templates", json=VALID_TEMPLATE)
    response = client.get("/workflow-templates")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_template_not_found(client, mock_llm):
    response = client.get(f"/workflow-templates/{uuid.uuid4()}")
    assert response.status_code == 404


def test_regression_report_not_found(client, mock_llm):
    response = client.get("/workflow-templates/regression?name=nonexistent")
    assert response.status_code == 404


def test_regression_report_with_no_runs_yet(client, mock_llm):
    client.post("/workflow-templates", json=VALID_TEMPLATE)

    response = client.get(f"/workflow-templates/regression?name={VALID_TEMPLATE['name']}")

    assert response.status_code == 200
    body = response.json()
    assert len(body["points"]) == 1
    assert body["points"][0]["run_count"] == 0
    assert body["points"][0]["avg_rule_score"] is None


def test_regression_report_across_two_versions(client, mock_llm):
    v1 = client.post("/workflow-templates", json={**VALID_TEMPLATE, "channel": "voice_simulated"}).json()
    v2 = client.post(
        "/workflow-templates", json={**VALID_TEMPLATE, "channel": "voice_simulated", "version": 2}
    ).json()

    campaign_v1 = client.post("/campaigns", json={"workflow_template_id": v1["id"], "name": "c1"}).json()
    campaign_v2 = client.post("/campaigns", json={"workflow_template_id": v2["id"], "name": "c2"}).json()
    contact = client.post("/contacts", json={"name": "Jane"}).json()

    mock_llm.responses.append(VALID_SCRIPT_JSON)
    run_v1 = client.post("/runs", json={"campaign_id": campaign_v1["id"], "contact_id": contact["id"]}).json()
    mock_llm.responses.append(VALID_JUDGE_JSON)
    client.post(f"/evals/{run_v1['id']}")

    mock_llm.responses.append(VALID_SCRIPT_JSON)
    run_v2 = client.post("/runs", json={"campaign_id": campaign_v2["id"], "contact_id": contact["id"]}).json()
    mock_llm.responses.append(VALID_JUDGE_JSON)
    client.post(f"/evals/{run_v2['id']}")

    response = client.get(f"/workflow-templates/regression?name={VALID_TEMPLATE['name']}")

    assert response.status_code == 200
    points = response.json()["points"]
    assert len(points) == 2
    assert points[0]["version"] == 1
    assert points[1]["version"] == 2
    assert points[0]["run_count"] == 1
    assert points[1]["run_count"] == 1
