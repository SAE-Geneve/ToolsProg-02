from fastapi.testclient import TestClient
from main import app

secret_token = "clown"
client = TestClient(app)

def test_get_player():
    response = client.post(
        "/p/",
        headers={"X-Token": secret_token},
        json={"id": "1", "name": "Player1"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Player1",
        "elo": 0,
    }

def test_get_or_create_player():
    response = client.get(
        "/p/get/Robert",
        headers={"X-Token": secret_token}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 4,
        "name": "Robert",
        "elo": 0,
    }


def test_get_or_create_game():
    response = client.get(
        "/g/get/2",
        headers={"X-Token": secret_token}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "state": "Finished"
    }