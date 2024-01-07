from fastapi import APIRouter, Response, status
from sqlmodel import Session
from ..core.database import engine
from ..models.room import Room, RoomCreate, RoomRead

router = APIRouter()


@router.post('/room')
async def create_room(room: RoomCreate, response: Response):
    with Session(engine) as session:
        db_room = session.get(Room, room.room_id)
        if db_room is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'error': 'Room already exists'}

        new_room = Room.from_orm(room)
        session.add(new_room)
        session.commit()
        session.refresh(new_room)
        response.status_code = status.HTTP_201_CREATED
        return {'message': f'Room {room.room_id} created successfully'}


@router.get('/room/{room_id}', response_model=RoomRead)
async def get_room(room_id: int):
    with Session(engine) as session:
        return session.get(Room, room_id)
