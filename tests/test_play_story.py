from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models.story import Story


# Test to play a story
def test_play_story(session: Session, client: TestClient):
    # Prepare by creating a user and a story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
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
    response = client.post('/story/1/join', json={'story_id': 1, 'character_id': character_id})
    assert response.status_code == 200

    # Play story
    response = client.post('/story/1/play', json={'story_id': 1, 'character_id': character_id})
    assert response.status_code == 200
    db_story = session.get(Story, 1)
    assert db_story
    assert db_story.active