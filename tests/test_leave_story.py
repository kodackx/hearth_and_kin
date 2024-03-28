from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character


# Test to leave a story
def test_leave_story(session: Session, client: TestClient):
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        # Prepare by creating a user, a story, and joining the story
        _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
        character_data = {
            "username": "test_user",
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
        character = client.post('/createcharacter', json=character_data)
        character_id = character.json()['character_id']
        story = client.post('/story', json={'creator': character_id, 'story_id': 1})
        story_id = story.json()['story_id']
        _ = client.post(f'/story/{story_id}/join', json={'story_id': story_id, 'character_id': character_id})
       

        # Leave story
        response = client.post(f'/story/{story_id}/leave', json={'story_id': story_id, 'character_id': character_id})

        # Verify story left
        assert response.status_code == 200
        character = session.get(Character, character_id)
        assert character is not None
        assert character.story_id is None

        # Leave non-existent story
        _ = client.post(f'/story/{story_id}/join', json={'story_id': story_id, 'character_id': character_id})
        response = client.post(f'/story/{story_id + 1}/leave', json={'story_id': story_id + 1, 'character_id': character_id})

        # Verify story not left
        assert response.status_code == 404
        character = session.get(Character, character_id)
        assert character is not None
        assert character.story_id is not None
