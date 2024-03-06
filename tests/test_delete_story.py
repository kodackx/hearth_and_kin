from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.story import Story
from src.models.user import User


# Test to delete a story successfully
def test_delete_story_success(session: Session, client: TestClient):
    # Prepare by creating a user
    response = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    assert response.status_code == 201

    # Add story
    response = client.post('/story', json={'creator': 'test_user', 'story_id': 1})

    # Verify story added
    assert response.status_code == 201
    assert session.get(Story, 1) is not None

    # Delete story
    response = client.request('DELETE', '/story/1', json={'story_id': 1})

    # Verify story deleted
    assert response.status_code == 200
    assert session.get(Story, 1) is None

    # Verify user not is deleted story
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.story_id is None


# Test to delete a story that does not exist
def test_delete_story_not_found(session: Session, client: TestClient):
    # Prepare by creating a user
    response = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    assert response.status_code == 201

    response = client.request('DELETE', '/story/99', json={'story_id': 99, 'username': 'test_user'})
    assert response.status_code == 404


# Test to delete a story that you are not the creator of
def test_delete_story_not_creator(session: Session, client: TestClient):
    # Prepare by creating two users, a story, and join one story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/user', json={'password': 'test', 'username': 'another_user'})
    _ = client.post('/story', json={'creator': 'test_user', 'story_id': 1})
    _ = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1})

    # Try to delete story you did not create
    response = client.request('DELETE', '/story/1', json={'story_id': 1, 'username': 'another_user'})

    # Verify story not deleted
    assert response.status_code == 404
    assert session.get(Story, 1) is not None

    # Verify user still in story
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.story_id == 1
