from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.user import User


# Test to join a story
def test_join_story(session: Session, client: TestClient):
    # Prepare by creating a user and a story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        
        # this now needs a character to be created
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
        character = client.post('/createcharacter', json=character_data)
        character_id = character.json()['character_id']
        _ = client.post('/story', json={'creator': character_id, 'story_id': 1})
    # Join story
    response = client.post('/story/1/join', json={'story_id': 1, 'character_id': 1})
    assert response.status_code == 200



     # Create a second story
    _ = client.post('/story', json={'creator': character_id, 'story_id': 2})


    character = session.get(Character, character_id)
    assert character is not None
    assert character.story_id == 1


# Test to join a story
def test_join_story_multiple_users(session: Session, client: TestClient):
    # Prepare by creating a user and a story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user_two'})
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
    character_id_one = character.json()['character_id']

    character_data = {
            "username": "test_user_two",
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
    character_id_two = character.json()['character_id']
    
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        _ = client.post('/story', json={'creator': character_id_one, 'story_id': 1})

    # Join story
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        response = client.post('/story/1/join', json={'character_id': character_id_one, 'story_id': 1})
        assert response.status_code == 200
        response = client.post('/story/1/join', json={'character_id': character_id_two, 'story_id': 1})
        assert response.status_code == 200

    # Verify both characters are in story
    character = session.get(Character, character_id_one)
    assert character is not None
    assert character.story_id == 1

    character = session.get(Character, character_id_two)
    assert character is not None
    assert character.story_id == 1
