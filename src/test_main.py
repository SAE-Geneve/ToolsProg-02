from fastapi.testclient import TestClient
from src.main import app

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

