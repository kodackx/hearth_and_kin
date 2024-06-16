from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import SQLModel
from fastapi.encoders import jsonable_encoder
from .config import logger  # noqa: F401


class WebsocketManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, story_id: int) -> None:
        logger.debug(f'Connecting to story_id {story_id}')
        await websocket.accept()
        try:
            self.active_connections[story_id].add(websocket)
            logger.debug(self.active_connections)
        except KeyError:
            self.active_connections[story_id] = set([websocket])
            logger.debug(self.active_connections)

    async def disconnect(self, websocket: WebSocket, story_id: int) -> None:
        if self.active_connections.get(story_id):
            self.active_connections[story_id].remove(websocket)

    async def broadcast(self, action: str, payload: dict | SQLModel, story_id: int) -> None:
        logger.debug(f'Received {action} to story_id {story_id}')
        if isinstance(payload, SQLModel):
            payload = jsonable_encoder(payload)
        message = {'action': action, 'data': payload}
        if story_id in self.active_connections:
            for connection in self.active_connections[story_id]:
                if connection.client_state.CONNECTED:
                    try:
                        await connection.send_json(message)
                    except RuntimeError: # Happens If some connection is closed already
                        logger.debug(f'Tried to send message to a closed client in story {story_id}')
                        pass

    
    async def endpoint(self, websocket: WebSocket, story_id: int) -> None:
        await self.connect(websocket, story_id)
        try:
            while True:
                message = await websocket.receive_json()
                await self.broadcast(message['action'], message['data'], story_id)
        
        except WebSocketDisconnect:
            logger.debug(f"Client disconnected from story {story_id}")
        finally:
            await self.disconnect(websocket, story_id)

def get_socket():
    websocket = WebsocketManager()
    yield websocket