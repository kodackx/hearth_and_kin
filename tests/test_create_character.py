from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character


# Test to create a character
def test_create_character(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})

    # Try create character
    response = client.post(
        '/character',
        json={
            'username': 'test_user',
            'user_description': 'desc',
            'goal': 'to find the secret',
            'charisma': 5,
        },
    )

    # Verify character added
    assert response.status_code == 201
    character = session.get(Character, 1)
    assert character is not None
    # TODO:make this dynamic
    assert character.charisma == 5
    assert character.goal == 'to find the secret'

    # Try add a cduplicate character
    # response = client.post('/character', json={'username': 'test_user', 'user_description': 'desc'})
    # assert response.status_code == 400


# Test to get a character
def test_get_character(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post(
        '/character',
        json={
            'username': 'test_user',
            'user_description': 'desc',
            'goal': 'to find the secret',
            'charisma': 5,
        },
    )

    # Try get character
    response = client.get('/user/test_user/characters')
    assert response.status_code == 200

    # Try add a cduplicate character
    # response = client.post('/character', json={'username': 'test_user', 'user_description': 'desc'})
    # assert response.status_code == 400


# Test to update a character
def test_update_character(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})

    # Create character
    _ = client.post(
        '/character',
        json={
            'username': 'test_user',
            'user_description': 'desc',
            'goal': 'to find the secret',
            'charisma': 5,
        },
    )

    # Update character
    response = client.patch(
        '/character/1',
        json={
            'username': 'test_user',
            'user_description': 'new desc',
            'goal': 'to find the new secret',
            'charisma': 1,
        },
    )

    # Verify character updated
    assert response.status_code == 201
    character = session.get(Character, 1)
    assert character is not None
    # TODO:make this dynamic
    assert character.charisma == 1
    assert character.goal == 'to find the new secret'
