from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.story import Story


# Test to create a story
def test_create_story(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})

    # Try create story
    response = client.post('/story', json={'creator': 'test_user', 'story_id': 1})

    # Verify story added
    assert response.status_code == 201
    assert session.get(Story, 1) is not None

    # Try add a duplicate story
    response = client.post('/story', json={'creator': 'test_user', 'story_id': 1})
    assert response.status_code == 400
