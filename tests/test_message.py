from unittest.mock import AsyncMock, patch
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.message import Message, MessagePC
from src.core.config import logger
from tests.test_create_character import create_character
from tests.test_create_story import create_story
from tests.test_create_user import create_user

@pytest.mark.asyncio
def test_websocket(session: Session, client: TestClient):
    user = create_user(client, session)
    character = create_character(client, session, user)
    story = create_story(client, session, character)
            
    # Define the mock return values for genAI mocks
    mock_image_path = '/path/to/mock/image.jpg'
    mock_narrator_reply = 'This is a mock reply'
    mock_audio = '/path/to/mock/narration.mp3'
    mock_soundtrack_path = '/path/to/mock/soundtrack.mp3'

    with client.websocket_connect(f"/ws/story/{story.story_id}") as websocket, \
        patch('src.services.narrator.generate_reply', return_value=(mock_narrator_reply, mock_soundtrack_path)), \
        patch('src.api.message.generate_audio', return_value=mock_audio), \
        patch('src.services.imagery.generate_image', return_value=mock_image_path):
        
        player_message = 'I open my eyes to the world'
        message = MessagePC.model_validate({
            'story_id': story.story_id,
            'character_name': character.character_name,
            'character_id': character.character_id,
            'portrait_path': character.portrait_path,
            'character': 'PC',
            'message': player_message
        })
        response = client.post('/message', json=message.model_dump(exclude={'timestamp'}))
        
        assert response.status_code == 200, 'Message should be created successfully'

        websocket_response = websocket.receive_json()
        assert websocket is not None, 'Websocket should receive a message'
        assert websocket_response['action'] == 'message', 'Websocket should receive a message action'
        assert websocket_response['data']['message'] == player_message, 'Websocket should receive the player message'
        assert websocket_response['data']['character_name'] == character.character_name, 'Websocket should receive the character name'

        narrator_message = session.get(Message, 2)  
        logger.debug(f'Narrator message: {narrator_message}')              
        assert narrator_message is not None, 'Narrator message should be created'
        assert narrator_message.character == 'NARRATOR', 'Narrator message should be from the narrator'
        assert narrator_message.message == mock_narrator_reply, 'Narrator message should be the mock reply'
        assert narrator_message.story_id == story.story_id, 'Narrator message should be in the story'
        assert narrator_message.audio_path == mock_audio, 'Narrator message should have an audio path'
        assert narrator_message.soundtrack_path == mock_soundtrack_path, 'Narrator message should have a soundtrack path'
        assert narrator_message.image_path == mock_image_path, 'Narrator message should have an image path'
