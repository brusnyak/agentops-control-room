def test_inbound_webhook_logs_event(client, mock_llm):
    response = client.post(
        "/webhooks/inbound",
        json={"event_type": "call.completed", "data": {"foo": "bar"}},
        headers={"x-provider": "test-provider"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "received"
