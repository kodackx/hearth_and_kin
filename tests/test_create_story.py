from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import CharacterRead
from src.models.story import Story, StoryRead
from tests.test_create_user import create_user
from tests.test_create_character import create_character
from unittest.mock import patch, AsyncMock


def create_story(client: TestClient, session: Session, character: CharacterRead, story_data: dict | None = None) -> StoryRead:
    # Create story
    story_data = story_data or {}
    story_data['party_lead'] = character.character_id
    
    response = client.post('/story', json=story_data)
    
    assert response.status_code == 201, 'Story should be created successfully'
    story = response.json()
    story = session.get(Story, story['story']['story_id'])
    assert story is not None
    return StoryRead.model_validate(story)

# Test to create a story
def test_create_story(session: Session, client: TestClient):
    user = create_user(client, session)
    character = create_character(client, session, user)
    #with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
    # Try create story
    story = create_story(client, session, character)

# TODO: add more tests 