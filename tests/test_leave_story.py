from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.user import User


# Test to leave a story
def test_leave_story(session: Session, client: TestClient):
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        # Prepare by creating a user, a story, and joining the story
        _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
        _ = client.post('/story', json={'creator': 'test_user', 'story_id': 1})
        character_data = {
        "character_id": 1,
        "username": "hero123",
        "character_name": "Gallant Knight",
        "description": "A brave knight seeking adventure.",
        "strength": 5,
        "dexterity": 4,
        "constitution": 5,
        "intelligence": 3,
        "wisdom": 2,
        "charisma": 4,
        "location": "The kingdom of Farland",
        "goal": "To save the kingdom from the dragon"
    }
        _ = client.post('/createcharacter', json=character_data)
        _ = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})

        # Leave story
        response = client.post('/story/1/leave', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})

        # Verify story left
        assert response.status_code == 200
        user = session.get(User, 'test_user')
        assert user is not None
        assert user.story_id is None

        # Leave non-existent story
        _ = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})
        response = client.post('/story/2/leave', json={'username': 'test_user', 'story_id': 2, 'character_id': 1})

        # Verify story not left
        assert response.status_code == 404
        user = session.get(User, 'test_user')
        assert user is not None
        assert user.story_id == 1
