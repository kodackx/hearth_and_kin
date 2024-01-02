from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.room import Room
from src.models.user import User


# Test to delete a room successfully
def test_delete_room_success(session: Session, client: TestClient):
    # Prepare by creating a user
    response = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    assert response.status_code == 201

    # Add room
    response = client.post('/room', json={'creator': 'test_user', 'room_id': 1})

    # Verify room added
    assert response.status_code == 201
    assert session.get(Room, 1) is not None

    # Delete room
    response = client.request('DELETE', '/room/1', json={'room_id': 1, 'username': 'test_user'})

    # Verify room deleted
    assert response.status_code == 200
    assert session.get(Room, 1) is None

    # Verify user not is deleted room
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.room_id is None


# Test to delete a room that does not exist
def test_delete_room_not_found(session: Session, client: TestClient):
    # Prepare by creating a user
    response = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    assert response.status_code == 201

    response = client.request('DELETE', '/room/99', json={'room_id': 99, 'username': 'test_user'})
    assert response.status_code == 404


# Test to delete a room that you are not the creator of
def test_delete_room_not_creator(session: Session, client: TestClient):
    # Prepare by creating two users, a room, and join one room
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/user', json={'password': 'test', 'username': 'another_user'})
    _ = client.post('/room', json={'creator': 'test_user', 'room_id': 1})
    _ = client.post('/room/1/join', json={'username': 'test_user', 'room_id': 1})

    # Try to delete room you did not create
    response = client.request('DELETE', '/room/1', json={'room_id': 1, 'username': 'another_user'})

    # Verify room not deleted
    assert response.status_code == 404
    assert session.get(Room, 1) is not None

    # Verify user still in room
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.room_id == 1
