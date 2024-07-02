from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character, CharacterRead
from src.models.user import UserRead
from tests.test_create_user import create_user


default_character_data = {
    'description': 'desc',
    'stat_cha': 5,
}


def create_character(client: TestClient, session: Session, user: UserRead, character_data: dict | None = None) -> CharacterRead:
    # Create character
    character_data = character_data or default_character_data
    character_data['user_id'] = user.user_id
    response = client.post('/createcharacter', json=character_data)
    assert response.status_code == 201, 'Character should be created successfully'
    character = response.json()
    character = session.get(Character, character['character_id'])
    assert character is not None
    return CharacterRead.model_validate(character)

# Test to create a character
def test_create_character(session: Session, client: TestClient) -> CharacterRead:
    character_data = default_character_data
    # Create a user first
    user = create_user(client, session)
    # Create character
    character = create_character(client, session, user, character_data)
    return character


# Test to update a character
def test_update_character(session: Session, client: TestClient):
    character = test_create_character(session, client)

    new_character_data = character.model_dump()
    new_character_data['description'] = 'new desc'
    new_character_data['stat_cha'] = 1

    response = client.patch(
        f'/character/{character.character_id}',
        json=new_character_data,
    )

    # Verify character updated
    assert response.status_code == 201, 'Character should be updated successfully'
    updated_character = session.get(Character, character.character_id)
    assert updated_character is not None
    assert updated_character != character, 'Character should be updated with new data'
    assert updated_character.stat_cha == new_character_data['stat_cha'], 'Character stat_cha should be updated'
    assert updated_character.description == new_character_data['description'], 'Character description should be updated'
