from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from tests.conftest import character_test_data


# Test to create a character
def test_create_character(characters: list[Character]):
    for i, character in enumerate(characters):
        assert character.character_name == character_test_data[i]['character_name'], 'Character should be created with the requested character_name'
        assert character.description == character_test_data[i]['description'], 'Character should be created with the requested description'


# Test to update a character
def test_update_character(
    session: Session, 
    client: TestClient, 
    get_token: list[dict[str, str]],
    characters: list[Character]
):
    character1, character2 = characters
    new_character_data = character1.model_dump()
    new_character_data['description'] = 'new desc'
    new_character_data['stat_cha'] = 1

    response = client.patch(
        f'/character/{character1.character_id}',
        json=new_character_data,
        headers=get_token[0]
    )

    # Verify character updated
    assert response.status_code == 201, 'Character should be updated successfully'
    updated_character = session.get(Character, character1.character_id)
    assert updated_character is not None
    assert updated_character.stat_cha == new_character_data['stat_cha'], 'Character stat_cha should be updated'
    assert updated_character.description == new_character_data['description'], 'Character description should be updated'


def test_update_incorrect_character(
    session: Session, 
    client: TestClient, 
    get_token: list[dict[str, str]],
    characters: list[Character]
):
    character1, character2 = characters
    new_character_data = character1.model_dump()

    response = client.patch(
        f'/character/{character1.character_id}',
        json=new_character_data,
        headers={'Authorization': 'Bearer invalid_token'}
    )

    assert response.status_code == 401, 'Character endpoint should refuse an invalid token'

    response = client.patch(
        f'/character/{character1.character_id}',
        json=new_character_data,
        headers=get_token[1]
    )

    assert response.status_code == 403, 'Character endpoint should refuse to update a character that does not belong to the user'
