from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.story import Story


# Test to join a story
def test_join_story_incorrect_token(session: Session, client: TestClient, characters: list[Character], stories: list[Story]):
    character1, character2 = characters
    story1 = stories[0]
    # Join story
    response = client.post(f'/story/{story1.story_id}/add_player', json={'character_id': character2.character_id, 'story_id': story1.story_id}, headers={'Authorization': 'Bearer incorrect_token'})
    assert response.status_code == 401, 'Should return 401 if token is incorrect'

# Test to join a story
def test_join_story_users(session: Session, client: TestClient, characters: list[Character], stories: list[Story], get_token: list[dict[str, str]]):
    character1, character2 = characters
    story1 = stories[0]
    headers1 = get_token[0]
    # Join story
    response = client.post(f'/story/{story1.story_id}/add_player', json={'character_id': character2.character_id, 'story_id': story1.story_id}, headers=headers1)
    assert response.status_code == 200

    # Verify both characters are in story
    joined_story = session.get(Story, story1.story_id)
    assert joined_story is not None
    assert joined_story.party_lead == character1.character_id, 'Story should have a party lead'
    assert joined_story.party_member_1 == character2.character_id, 'Story should have a member'
