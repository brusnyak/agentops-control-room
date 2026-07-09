import uuid

VALID_TEMPLATE = {
    "name": "Lead follow-up",
    "channel": "email",
    "goal_prompt": "Follow up on a demo request",
    "eval_rubric": "Pass if brief and proposes a next step",
}


def test_create_template(client, mock_llm):
    response = client.post("/workflow-templates", json=VALID_TEMPLATE)
    assert response.status_code == 201
    assert response.json()["channel"] == "email"


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
