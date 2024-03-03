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
        except KeyError:
            self.active_connections[story_id] = set([websocket])

    async def disconnect(self, websocket: WebSocket, story_id: int) -> None:
        logger.debug(f'Disconnecting ws from story_id {story_id}')
        #self.active_connections[story_id].remove(websocket)
        #if websocket.client_state.CONNECTED:
        #    await websocket.close()
        logger.debug(f'Disconnecting ws from story_id {story_id} complete')

    async def broadcast(self, action: str, payload: dict | SQLModel, story_id: int) -> None:
        logger.debug(f'Received broadcast command to story_id {story_id}')
        if isinstance(payload, SQLModel):
            payload = jsonable_encoder(payload)
        message = {'action': action, 'data': payload}
        logger.debug(f'active connectins: {self.active_connections[story_id]}')
        for connection in self.active_connections[story_id]:
            if connection.client_state.CONNECTED:
                logger.debug(f'sending to story_id {story_id}')
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
            await self.disconnect(websocket, story_id)

def get_socket():
    websocket = WebsocketManager()
    yield websocket