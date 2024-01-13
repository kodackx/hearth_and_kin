from fastapi import WebSocket
from sqlmodel import SQLModel
from fastapi.encoders import jsonable_encoder


class WebsocketManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, action: str, payload: dict | SQLModel) -> None:
        if isinstance(payload, SQLModel):
            payload = jsonable_encoder(payload)
        message = {'action': action, 'data': payload}
        for connection in self.active_connections:
            await connection.send_json(message)

def get_socket():
    websocket = WebsocketManager()
    yield websocket