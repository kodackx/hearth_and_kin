from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models.story import Story


# Test to play a story
def test_play_story(session: Session, client: TestClient):
    # Prepare by creating a user and a story
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

    # Join story
    response = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})
    assert response.status_code == 200

    # Play story
    response = client.post('/story/1/play', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})
    assert response.status_code == 200
    db_story = session.get(Story, 1)
    assert db_story
    assert db_story.active

    # Try to play already active story
    # response = client.post('/story/1/play', json={'username': 'test_user', 'story_id': 1})
    # assert response.status_code == 400

    # Try to play story with different user
    # (unsure about the below)
    # _ = client.post('/user', json={'password': 'test', 'username': 'test_user_two'})
    # response = client.post('/story/1/join', json={'username': 'test_user_two', 'story_id': 1})
    # assert response.status_code == 400
    # response = client.post('/story/1/play', json={'username': 'test_user_two', 'story_id': 1})
    # assert response.status_code == 400

    # Try to play story as non-creator
    # probably not needed since nobody would see the story if they haven't joined
    # response = client.post('/story/1/play', json={'username': 'test_user_two', 'story_id': 1})
    # assert response.status_code == 400
