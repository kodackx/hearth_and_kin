from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.character import Character
from src.models.story import Story


# Test to delete a story successfully
def test_delete_story_success(session: Session, client: TestClient, characters: list[Character], stories: list[Story], get_token: list[dict[str, str]]):
    story1 = stories[0]
    # Delete story
    response = client.request('DELETE', f'/story/{story1.story_id}', json={'story_id': story1.story_id, 'character_id': characters[0].character_id}, headers=get_token[0])

    # Verify story deleted
    assert response.status_code == 200
    assert session.get(Story, story1.story_id) is None


# Test to delete a story that does not exist
def test_delete_story_not_found(client: TestClient, characters: list[Character], stories: list[Story], get_token: list[dict[str, str]]):
    story1 = stories[0]
    response = client.request('DELETE', f'/story/{story1.story_id + 1}', json={'story_id': story1.story_id + 1, 'character_id': characters[0].character_id}, headers=get_token[0])
    assert response.status_code == 404, 'Story should not be found'


# Test to delete a story that you are not the creator of
def test_delete_story_not_creator(session: Session, client: TestClient, characters: list[Character], stories: list[Story], get_token: list[dict[str, str]]):
    story1 = stories[0]
    # Join the story with character2
    _ = client.post(f'/story/{story1.story_id}/add_player', json={'story_id': story1.story_id, 'character_id': characters[1].character_id}, headers=get_token[1])

    # Try to delete story you did not create
    response = client.request('DELETE', f'/story/{story1.story_id}', json={'story_id': story1.story_id, 'character_id': characters[1].character_id}, headers=get_token[1])

    # Verify story not deleted
    assert response.status_code == 404
    assert session.get(Story, story1.story_id) is not None
