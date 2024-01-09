from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.message import MessageBase, MessageCreate

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

    with client.websocket_connect("/ws/prompt") as websocket:
        message = MessageCreate.model_validate({
            'story_id': 1,
            'username': 'test_user',
            'character_id': 1,
            'message': 'I open my eyes'
        })
        websocket.send_json(message.model_dump(exclude='timestamp'))
        data = websocket.receive_json()