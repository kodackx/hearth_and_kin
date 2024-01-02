from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.user import User


# Test to join a room
def test_join_room(session: Session, client: TestClient):
    # Prepare by creating a user and a room
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/room', json={'creator': 'test_user', 'room_id': 1})

    # Join room
    response = client.post('/room/1/join', json={'username': 'test_user', 'room_id': 1})
    assert response.status_code == 200

    # Cant join already joined room
    response = client.post('/room/1/join', json={'username': 'test_user', 'room_id': 1})
    assert response.status_code == 400

    # Create a second room
    _ = client.post('/room', json={'creator': 'test_user', 'room_id': 2})

    # Cant join second room while in first
    response = client.post('/room/2/join', json={'username': 'test_user', 'room_id': 2})
    assert response.status_code == 400

    user = session.get(User, 'test_user')
    assert user is not None
    assert user.room_id == 1


# Test to join a room
def test_join_room_multiple_users(session: Session, client: TestClient):
    # Prepare by creating a user and a room
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user_two'})
    _ = client.post('/room', json={'creator': 'test_user', 'room_id': 1})

    # Join room
    response = client.post('/room/1/join', json={'username': 'test_user', 'room_id': 1})
    assert response.status_code == 200
    response = client.post('/room/1/join', json={'username': 'test_user_two', 'room_id': 1})
    assert response.status_code == 200

    # Verify both users are in room
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.room_id == 1

    user = session.get(User, 'test_user_two')
    assert user is not None
    assert user.room_id == 1
