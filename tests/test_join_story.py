from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.story import Story
from src.models.user import User


# Test to join a story
def test_join_story_users(session: Session, client: TestClient, user: User, user2: User, character: Character, character2: Character, story: Story):
    # Prepare by creating two users, a story, and join one story

    # Join story
    response = client.post(f'/story/{story.story_id}/add_player', json={'character_id': character2.character_id, 'story_id': story.story_id})
    assert response.status_code == 200

    # Verify both characters are in story
    joined_story = session.get(Story, story.story_id)
    assert joined_story is not None
    assert joined_story.party_lead == character.character_id, 'Story should have a party lead'
    assert joined_story.party_member_1 == character2.character_id, 'Story should have a member'
