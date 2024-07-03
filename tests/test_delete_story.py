from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.story import Story
from unittest.mock import patch, AsyncMock

from tests.test_create_character import create_character
from tests.test_create_story import create_story
from tests.test_create_user import create_user


# Test to delete a story successfully
def test_delete_story_success(session: Session, client: TestClient):
    user = create_user(client, session)
    character = create_character(client, session, user)
    story = create_story(client, session, character)

    # Delete story
    response = client.request('DELETE', f'/story/{story.story_id}', json={'story_id': story.story_id, 'character_id': character.character_id})

    # Verify story deleted
    assert response.status_code == 200
    assert session.get(Story, story.story_id) is None


# Test to delete a story that does not exist
def test_delete_story_not_found(session: Session, client: TestClient):
    user = create_user(client, session)
    character = create_character(client, session, user)

    response = client.request('DELETE', '/story/1', json={'story_id': 1, 'character_id': character.character_id})
    assert response.status_code == 404


# Test to delete a story that you are not the creator of
def test_delete_story_not_creator(session: Session, client: TestClient):
    # Prepare by creating two users, a story, and join one story
    user1= create_user(client, session)
    user2 = create_user(client, session, user_data={'username': 'user2'})

    character1 = create_character(client, session, user1)
    character2 = create_character(client, session, user2)

    story = create_story(client, session, character1)
    
    # Join the story with character2
    _ = client.post(f'/story/{story.story_id}/add_player', json={'story_id': story.story_id, 'character_id': character2.character_id})

    # Try to delete story you did not create
    response = client.request('DELETE', f'/story/{story.story_id}', json={'story_id': story.story_id, 'character_id': character2.character_id})

    # Verify story not deleted
    assert response.status_code == 404
    assert session.get(Story, story.story_id) is not None
