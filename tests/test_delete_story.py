from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.story import Story
from unittest.mock import patch, AsyncMock


# Test to delete a story successfully
def test_delete_story_success(session: Session, client: TestClient):
    # Prepare by creating a user
    response = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    assert response.status_code == 201

    response = client.post('/createcharacter', json={ 'username': 'test_user', 'character_name': 'char', 'description': 'desc', 'goal': 'to find the secret', 'charisma': 5})
    assert response.status_code == 201
    character = response.json()['character_id']

    # Add story
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        response = client.post('/story', json={'creator': character, 'story_id': 1})

    # Verify story added
    assert response.status_code == 201
    assert session.get(Story, 1) is not None

    # Delete story
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        response = client.request('DELETE', '/story/1', json={'story_id': 1, 'character_id': character})

    # Verify story deleted
    assert response.status_code == 200
    assert session.get(Story, 1) is None

    # Verify user not is deleted story
    character = session.get(Character, character)
    assert character is not None
    assert character.story_id is None


# Test to delete a story that does not exist
def test_delete_story_not_found(session: Session, client: TestClient):
    # Prepare by creating a user
    response = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    assert response.status_code == 201

    response = client.post('/createcharacter', json={ 'username': 'test_user', 'character_name': 'char', 'description': 'desc', 'goal': 'to find the secret', 'charisma': 5})
    assert response.status_code == 201
    character = response.json()['character_id']

    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        response = client.request('DELETE', '/story/99', json={'story_id': 99, 'character_id': character})
    assert response.status_code == 404


# Test to delete a story that you are not the creator of
def test_delete_story_not_creator(session: Session, client: TestClient):
    # Prepare by creating two users, a story, and join one story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/user', json={'password': 'test', 'username': 'another_user'})

    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        # need to create character before joining a story
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
        _ = client.post('/story', json={'creator': 1, 'story_id': 1})
        _ = client.post('/story/1/join', json={'story_id': 1, 'character_id': 1})

        # Try to delete story you did not create
        response = client.request('DELETE', '/story/1', json={'story_id': 1, 'character_id': 2})

    # Verify story not deleted
    assert response.status_code == 404
    assert session.get(Story, 1) is not None
