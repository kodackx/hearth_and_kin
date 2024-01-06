from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.user import User


# Test to leave a story
def test_leave_story(session: Session, client: TestClient):
    # Prepare by creating a user, a story, and joining the story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/story', json={'creator': 'test_user', 'story_id': 1})
    _ = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1})

    # Leave story
    response = client.post('/story/1/leave', json={'username': 'test_user', 'story_id': 1})

    # Verify story left
    assert response.status_code == 200
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.story_id is None

    # Leave non-existent story
    _ = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1})
    response = client.post('/story/2/leave', json={'username': 'test_user', 'story_id': 2})

    # Verify story not left
    assert response.status_code == 404
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.story_id == 1