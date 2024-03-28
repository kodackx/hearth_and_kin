from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.story import Story
from unittest.mock import patch, AsyncMock


# Test to create a story
def test_create_story(session: Session, client: TestClient):
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
        character = client.post(
        '/createcharacter',
        json={
            'username': 'test_user',
            'character_name': 'char',
            'description': 'desc',
            'goal': 'to find the secret',
            'charisma': 5,
        },
    )
        # Try create story
        response = client.post('/story', json={'creator': character.json()['character_id'], 'story_id': 1})

        # Verify story added
        assert response.status_code == 201
        assert session.get(Story, 1) is not None

        # Try add a duplicate story
        response = client.post('/story', json={'creator': character.json()['character_id'], 'story_id': 1})
        assert response.status_code == 400
