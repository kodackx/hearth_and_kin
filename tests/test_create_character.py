from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character


# Test to create a character
def test_create_character(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})

    # Try create character
    response = client.post(
        '/createcharacter',
        json={
            'username': 'test_user',
            'description': 'desc',
            'goal': 'to find the secret',
            'charisma': 5,
        },
    )

    # Verify character added
    assert response.status_code == 201
    assert 'character_id' in response.json().keys(), response.json()
    character_id = response.json()['character_id']
    character = session.get(Character, character_id)
    assert character is not None
    # TODO:make this dynamic
    assert character.charisma == 5
    assert character.goal == 'to find the secret'

    # Try add a cduplicate character
    # response = client.post('/character', json={'username': 'test_user', 'user_description': 'desc'})
    # assert response.status_code == 400


# Test to update a character
def test_update_character(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})

    # Create character
    response = client.post(
        '/createcharacter',
        json={
            'username': 'test_user',
            'description': 'desc',
            'goal': 'to find the secret',
            'charisma': 5,
        },
    )
    character_id = response.json()['character_id']
    # Update character
    response = client.patch(
        f'/character/{character_id}',
        json={
            'username': 'test_user',
            'description': 'new desc',
            'goal': 'to find the new secret',
            'charisma': 1,
        },
    )

    # Verify character updated
    assert response.status_code == 201, response.json()
    character = session.get(Character, 1)
    assert character is not None
    # TODO:make this dynamic
    assert character.charisma == 1
    assert character.goal == 'to find the new secret'
