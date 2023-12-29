from fastapi import APIRouter, Response, status
from sqlmodel import Session, select

from src.models.user import User
from ..core.database import engine
from ..models.room import Room, RoomCreate, RoomRead, RoomUser

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


@router.get('/rooms')
async def get_rooms():
    with Session(engine) as session:
        return session.exec(select(Room)).all()


@router.get('/room/{room_id}', response_model=RoomRead)
async def get_room(room_id: int):
    with Session(engine) as session:
        return session.get(Room, room_id)


@router.post('/room/{room_id}/join')
async def join_room(room: RoomUser, response: Response):
    with Session(engine) as session:
        db_room = session.get(Room, room.room_id)
        db_user = session.get(User, room.username)
        if db_room is None or db_user is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'error': 'Room or user does not exist'}
        # if db_user.username == db_room.username:
        #    response.status_code = status.HTTP_400_BAD_REQUEST
        #    return {'error': f'User {room.username} is alredy in room {room.room_id}'}

        db_user.is_in_room = True
        db_user.room_id = room.room_id
        # db_room.users.append(db_user)s
        response.status_code = status.HTTP_200_OK
        return {'message': f'User {room.username} joined room {room.room_id}'}


@router.post('/room/{room_id}/leave')
async def leave_room(room: RoomUser, response: Response):
    with Session(engine) as session:
        db_room = session.get(Room, room.room_id)
        db_user = session.get(User, room.username)

        if db_room is None or db_user is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'error': 'Room or user does not exist'}
        # if db_user not in db_room.users:
        #    response.status_code = status.HTTP_400_BAD_REQUEST
        #    return {'error': f'User {room.username} is not in room {room.room_id}'}

        db_user.is_in_room = False
        db_user.room_id = None
        # db_room.users.remove(db_user)
        response.status_code = status.HTTP_200_OK
        return {'message': f'User {room.username} left room {room.room_id}'}
