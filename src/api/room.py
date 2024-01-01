from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select


from src.models.user import User
from ..core.database import engine
from ..models.room import Room, RoomCreate, RoomUser

router = APIRouter()


@router.post('/room', status_code=201)
async def create_room(room: RoomCreate):
    with Session(engine) as session:
        db_room = session.get(Room, room.room_id)
        if db_room is not None:
            raise HTTPException(400, 'Room already exists')

        new_room = Room.from_orm(room)
        session.add(new_room)
        session.commit()
        session.refresh(new_room)
        return {'message': f'Room {room.room_id} created successfully'}


@router.get('/rooms', response_model=list[Room])
async def get_rooms():
    with Session(engine) as session:
        return session.exec(select(Room)).all()


@router.get('/room/{room_id}', response_model=Room)
async def get_room(room_id: int):
    with Session(engine) as session:
        return session.get(Room, room_id)


@router.post('/room/{room_id}/join')
async def join_room(room: RoomUser):
    with Session(engine) as session:
        db_room = session.get(Room, room.room_id)
        db_user = session.get(User, room.username)
        if db_room is None or db_user is None:
            raise HTTPException(404, 'Room or user does not exist')
        db_user.room_id = db_room.room_id
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return {'message': f'User {room.username} joined room {room.room_id}'}


@router.post('/room/{room_id}/leave')
async def leave_room(room: RoomUser):
    with Session(engine) as session:
        statement = select(User).where(User.username == room.username).where(User.room_id == room.room_id)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(404, 'Room or user does not exist')

        user.room_id = None
        session.add(user)
        session.commit()
        session.refresh(user)

        return {'message': f'User {room.username} left room {room.room_id}'}
