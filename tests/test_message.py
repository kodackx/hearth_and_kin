from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.message import MessageCreate
from src.core.config import logger

def test_websocket(session: Session, client: TestClient):
    with patch('src.api.story.socket_manager.broadcast', new_callable=AsyncMock):
        _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
        character = client.post(
            '/createcharacter',
            json={
                'username': 'test_user',
                'user_description': 'desc',
                'goal': 'to find the secret',
                'charisma': 5,
            },
        )
        character_id = character.json()['character_id']
        _ = client.post('/story', json={'creator': character_id, 'story_id': 1})
        

    # TODO: figure out how to run this async
    #with client.websocket_connect("/ws/story/1") as websocket:
    message = MessageCreate.model_validate({
        'story_id': 1,
        'character_name': 'test_char',
        'character_id': character_id,
        'message': 'I open my eyes'
    })
    # TODO: figure out how to call this without calling openai
    #response = client.post('/message', json=message.model_dump(exclude='timestamp'))
    #logger.debug(response.json())
    #websocket_response = websocket.receive_json()
    
    #assert websocket_response.json()['action'] == 'message'
    #assert websocket_response.json()['data']['message'] == 'I open my eyes'
    #assert response.json()['narrator_reply'] == 'reply'