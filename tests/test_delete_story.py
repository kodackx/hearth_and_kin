from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.story import Story


# Test to delete a story successfully
def test_delete_story_success(session: Session, client: TestClient, character: Character, story: Story):
    # Delete story
    response = client.request('DELETE', f'/story/{story.story_id}', json={'story_id': story.story_id, 'character_id': character.character_id})

    # Verify story deleted
    assert response.status_code == 200
    assert session.get(Story, story.story_id) is None


# Test to delete a story that does not exist
def test_delete_story_not_found(client: TestClient, character: Character, story: Story):
    response = client.request('DELETE', f'/story/{story.story_id + 1}', json={'story_id': story.story_id + 1, 'character_id': character.character_id})
    assert response.status_code == 404, 'Story should not be found'


# Test to delete a story that you are not the creator of
def test_delete_story_not_creator(session: Session, client: TestClient, character2: Character, story: Story):
    # Join the story with character2
    _ = client.post(f'/story/{story.story_id}/add_player', json={'story_id': story.story_id, 'character_id': character2.character_id})

    # Try to delete story you did not create
    response = client.request('DELETE', f'/story/{story.story_id}', json={'story_id': story.story_id, 'character_id': character2.character_id})

    # Verify story not deleted
    assert response.status_code == 404
    assert session.get(Story, story.story_id) is not None
