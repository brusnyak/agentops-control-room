import uuid


def test_create_and_get_contact(client, mock_llm):
    response = client.post("/contacts", json={"name": "Jane Doe", "email": "jane@example.com"})
    assert response.status_code == 201
    contact = response.json()
    assert contact["name"] == "Jane Doe"

    fetched = client.get(f"/contacts/{contact['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "jane@example.com"


def test_list_contacts(client, mock_llm):
    client.post("/contacts", json={"name": "A"})
    client.post("/contacts", json={"name": "B"})

    response = client.get("/contacts")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_contact_not_found(client, mock_llm):
    response = client.get(f"/contacts/{uuid.uuid4()}")
    assert response.status_code == 404
