from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.room import Room


# Test to create a room
def test_create_room(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})

    # Try create room
    response = client.post('/room', json={'creator': 'test_user', 'room_id': 1})

    # Verify room added
    assert response.status_code == 201
    assert session.get(Room, 1) is not None

    # Try add a duplicate room
    response = client.post('/room', json={'creator': 'test_user', 'room_id': 1})
    assert response.status_code == 400
