from fastapi.testclient import TestClient
from sqlmodel import Session
from src.datamodels.character import Character
from src.datamodels.story import Story


# Test to leave a story
def test_leave_story(session: Session, client: TestClient, characters: list[Character], stories: list[Story]):
    character1, character2 = characters
    story1, story2 = stories
    _ = client.post(f'/story/{story1.story_id}/add_player', json={'story_id': story1.story_id, 'character_id': character1.character_id})
    _ = client.post(f'/story/{story1.story_id}/add_player', json={'story_id': story1.story_id, 'character_id': character2.character_id})

    # Try leave non-existent story
    response = client.post(f'/story/{story1.story_id + 99}/leave', json={'story_id': story1.story_id + 99, 'character_id': character2.character_id})

    # Verify existent story not left
    assert response.status_code == 404
    non_empty_story = session.get(Story, story1.story_id)        
    assert non_empty_story is not None
    assert non_empty_story.party_lead == character1.character_id, 'Story should not be left'
    assert non_empty_story.party_member_1 == character2.character_id, 'Story should not be left'

    # Leave story
    response = client.post(f'/story/{story1.story_id}/leave', json={'story_id': story1.story_id, 'character_id': character2.character_id})

    # Verify story left
    assert response.status_code == 200
    left_story = session.get(Story, story1.story_id)
    assert left_story is not None, 'Story should still exist'
    assert left_story.party_lead is not None, 'Story should still have a party lead'
    assert left_story.party_member_1 is None, 'Story should have no party members'
    assert left_story.party_member_2 is None, 'Story should have no party members'

