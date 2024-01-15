from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import SQLModel
from fastapi.encoders import jsonable_encoder
from .config import logger  # noqa: F401


class WebsocketManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, set[WebSocket]] = {0: set()}

    async def connect(self, websocket: WebSocket, story_id: int) -> None:
        await websocket.accept()
        try:
            self.active_connections[story_id].add(websocket)
        except KeyError:
            self.active_connections[story_id] = set()

    def disconnect(self, websocket: WebSocket) -> None:
        self.disconnect(websocket)

    async def broadcast(self, action: str, payload: dict | SQLModel, story_id: int) -> None:
        if isinstance(payload, SQLModel):
            payload = jsonable_encoder(payload)
        message = {'action': action, 'data': payload}
        for connection in self.active_connections[story_id]:
            await connection.send_json(message)
    
    async def endpoint(self, websocket: WebSocket, story_id: int) -> None:
        await self.connect(websocket, story_id)
        try:
            while True:
                message = await websocket.receive_json()
                await self.broadcast(message['action'], message['data'], story_id)
        
        except WebSocketDisconnect:
            self.disconnect(websocket)

def get_socket():
    websocket = WebsocketManager()
    yield websocket