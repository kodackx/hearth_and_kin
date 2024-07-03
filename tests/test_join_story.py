from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.story import Story
from tests.test_create_character import create_character
from tests.test_create_story import create_story
from tests.test_create_user import create_user


# Test to join a story
def test_join_story_users(session: Session, client: TestClient):
    # Prepare by creating two users, a story, and join one story
    user1 = create_user(client, session)
    user2 = create_user(client, session)
    character1 = create_character(client, session, user1)
    character2 = create_character(client, session, user2)

    story = create_story(client, session, character1)

    # Join story
    response = client.post(f'/story/{story.story_id}/add_player', json={'character_id': character2.character_id, 'story_id': story.story_id})
    assert response.status_code == 200

    # Verify both characters are in story
    joined_story = session.get(Story, story.story_id)
    assert joined_story is not None
    assert joined_story.party_lead == character1.character_id, 'Story should have a party lead'
    assert joined_story.party_member_1 == character2.character_id, 'Story should have a member'
