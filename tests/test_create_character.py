from fastapi.testclient import TestClient
from sqlmodel import Session
from src.datamodels.character import Character
from tests.conftest import character_test_data


# Test to create a character
def test_create_character(characters: list[Character]):
    for i, character in enumerate(characters):
        assert character.character_name == character_test_data[i]['character_name'], 'Character should be created with the requested character_name'
        assert character.description == character_test_data[i]['description'], 'Character should be created with the requested description'


# Test to update a character
def test_update_character(session: Session, client: TestClient, characters: list[Character]):
    character = characters[0]
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
    assert updated_character.stat_cha == new_character_data['stat_cha'], 'Character stat_cha should be updated'
    assert updated_character.description == new_character_data['description'], 'Character description should be updated'
