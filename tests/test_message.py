from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.message import MessageCreate
from src.core.config import logger

def test_websocket(session: Session, client: TestClient):
    _ = client.post('/user', json={'password': 'test', 'username': 'test_user'})
    _ = client.post('/story', json={'creator': 'test_user', 'story_id': 1})
    _ = client.post(
        '/character',
        json={
            'username': 'test_user',
            'user_description': 'desc',
            'goal': 'to find the secret',
            'charisma': 5,
        },
    )

    # TODO: figure out how to run this async
    #with client.websocket_connect("/ws/story/1") as websocket:
    message = MessageCreate.model_validate({
        'story_id': 1,
        'username': 'test_user',
        'character_id': 1,
        'message': 'I open my eyes'
    })
    response = client.post('/message', json=message.model_dump(exclude='timestamp'))
    #websocket_response = websocket.receive_json()
    
    #assert websocket_response.json()['action'] == 'message'
    #assert websocket_response.json()['data']['message'] == 'I open my eyes'
    assert response.json()['narrator_reply'] == 'reply'