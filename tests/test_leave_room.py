from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.user import User


# Test to leave a room
def test_leave_room(session: Session, client: TestClient):
    # Prepare by creating a user, a room, and joining the room
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/room', json={'creator': 'test_user', 'room_id': 1})
    _ = client.post('/room/1/join', json={'username': 'test_user', 'room_id': 1})

    # Leave room
    response = client.post('/room/1/leave', json={'username': 'test_user', 'room_id': 1})

    # Verify room left
    assert response.status_code == 200
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.room_id is None

    # Leave non-existent room
    _ = client.post('/room/1/join', json={'username': 'test_user', 'room_id': 1})
    response = client.post('/room/2/leave', json={'username': 'test_user', 'room_id': 2})

    # Verify room not left
    assert response.status_code == 404
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.room_id == 1
