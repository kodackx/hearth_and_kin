from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character


# Test to create a character
def test_create_character(character: Character):
    assert character is not None, 'Character should be created successfully via the fixture in conftest.py'


# Test to update a character
def test_update_character(session: Session, client: TestClient, character: Character):
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
