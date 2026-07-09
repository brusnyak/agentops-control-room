import uuid

import httpx

VALID_TEMPLATE = {
    "name": "Lead follow-up", "channel": "email",
    "goal_prompt": "Follow up", "eval_rubric": "Pass if clear",
}


def _fake_response(status_code: int) -> httpx.Response:
    request = httpx.Request("POST", "https://example.com/webhook")
    return httpx.Response(status_code=status_code, json={"ok": True}, request=request)


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


def test_export_campaign_not_found(client, mock_llm):
    response = client.post(f"/campaigns/{uuid.uuid4()}/export", json={"webhook_url": "https://example.com/hook"})
    assert response.status_code == 404


def test_export_campaign_success(client, mock_llm, monkeypatch):
    template = client.post("/workflow-templates", json=VALID_TEMPLATE).json()
    campaign = client.post("/campaigns", json={"workflow_template_id": template["id"], "name": "Campaign A"}).json()

    monkeypatch.setattr("app.routers.campaigns.httpx.post", lambda *a, **k: _fake_response(200))

    response = client.post(f"/campaigns/{campaign['id']}/export", json={"webhook_url": "https://example.com/hook"})

    assert response.status_code == 200
    body = response.json()
    assert body["delivered"] is True
    assert body["run_count"] == 0


def test_export_campaign_target_failure(client, mock_llm, monkeypatch):
    template = client.post("/workflow-templates", json=VALID_TEMPLATE).json()
    campaign = client.post("/campaigns", json={"workflow_template_id": template["id"], "name": "Campaign A"}).json()

    monkeypatch.setattr("app.routers.campaigns.httpx.post", lambda *a, **k: _fake_response(500))

    response = client.post(f"/campaigns/{campaign['id']}/export", json={"webhook_url": "https://example.com/hook"})

    assert response.status_code == 200
    body = response.json()
    assert body["delivered"] is False
    assert body["status_code"] == 500
