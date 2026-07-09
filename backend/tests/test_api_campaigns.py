import uuid

VALID_TEMPLATE = {
    "name": "Lead follow-up", "channel": "email",
    "goal_prompt": "Follow up", "eval_rubric": "Pass if clear",
}


def test_create_campaign(client, mock_llm):
    template = client.post("/workflow-templates", json=VALID_TEMPLATE).json()

    response = client.post("/campaigns", json={"workflow_template_id": template["id"], "name": "Campaign A"})

    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_create_campaign_template_not_found(client, mock_llm):
    response = client.post("/campaigns", json={"workflow_template_id": str(uuid.uuid4()), "name": "X"})
    assert response.status_code == 404


def test_list_campaigns(client, mock_llm):
    template = client.post("/workflow-templates", json=VALID_TEMPLATE).json()
    client.post("/campaigns", json={"workflow_template_id": template["id"], "name": "Campaign A"})

    response = client.get("/campaigns")
    assert response.status_code == 200
    assert len(response.json()) == 1
