from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.user import User


# Test to join a story
def test_join_story(session: Session, client: TestClient):
    # Prepare by creating a user and a story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/story', json={'creator': 'test_user', 'story_id': 1})
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
    _ = client.post('/createcharacter', json=character_data)

    # Join story
    response = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})
    assert response.status_code == 200

    # Cant join already joined story
    response = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})
    assert response.status_code == 400

    # Create a second story
    _ = client.post('/story', json={'creator': 'test_user', 'story_id': 2})

    # Cant join second story while in first
    # update march 6: i don't think this test makes sense anymore
    # response = client.post('/story/2/join', json={'username': 'test_user', 'story_id': 2})
    # assert response.status_code == 400

    user = session.get(User, 'test_user')
    assert user is not None
    assert user.story_id == 1


# Test to join a story
def test_join_story_multiple_users(session: Session, client: TestClient):
    # Prepare by creating a user and a story
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user_two'})
    _ = client.post('/story', json={'creator': 'test_user', 'story_id': 1})

    # Join story
    response = client.post('/story/1/join', json={'username': 'test_user', 'story_id': 1, 'character_id': 1})
    assert response.status_code == 200
    response = client.post('/story/1/join', json={'username': 'test_user_two', 'story_id': 1, 'character_id': 1})
    assert response.status_code == 200

    # Verify both users are in story
    user = session.get(User, 'test_user')
    assert user is not None
    assert user.story_id == 1

    user = session.get(User, 'test_user_two')
    assert user is not None
    assert user.story_id == 1
