from src.models.story import Story
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.user import User

# Test to remove the image model from a story
def test_update_story_model(client: TestClient, session: Session, stories: list[Story]):
    story1 = stories[0]

    response = client.post(f'/story/{story1.story_id}/update_models', json={'character_id': story1.party_lead, 'story_id': story1.story_id, 'genai_image_model': 'none'})
    assert response.status_code == 200, 'Model enum should reject invalid model'


    response = client.post(f'/story/{story1.story_id}/update_models', json={'character_id': story1.party_lead, 'story_id': story1.story_id, 'genai_text_model': 'mock'})
    assert response.status_code == 422, 'Model enum should reject invalid model'

    db_story = session.get(Story, story1.story_id)
    assert db_story is not None, 'Story should be found'
    assert db_story.genai_image_model == 'none', 'Story should have the updated image model'

# Test to add NVIDIA API key to user and update the story model
def test_update_story(client: TestClient, stories: list[Story], users: list[User]):
    user1 = users[0]
    story1 = stories[0]
    response = client.patch(f'/user/{user1.user_id}', json={'user_id': user1.user_id, 'nvidia_api_key': 'mock'})

    response = client.post(f'/story/{story1.story_id}/update_models', json={'character_id': story1.party_lead, 'story_id': story1.story_id, 'genai_text_model': 'nvidia'})
    assert response.status_code == 200, 'Story should be updated successfully'

    story = response.json()
    assert story['genai_text_model'] == 'nvidia', 'Story should have the updated text model'


def test_update_story_no_api_key(client: TestClient, stories: list[Story]):
    story1 = stories[0]
    response = client.post(f'/story/{story1.story_id}/update_models', json={'character_id': story1.party_lead, 'story_id': story1.story_id, 'genai_text_model': 'nvidia'})
    assert response.status_code == 400, 'Model update should be rejected if the user has no API key added'
