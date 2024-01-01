from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select


from src.models.user import User
from ..core.database import engine
from ..models.room import Room, RoomCreate, RoomJoin, RoomDelete

router = APIRouter()


@router.post('/room', status_code=201)
async def create_room(room: RoomCreate):
    with Session(engine) as session:
        db_room = session.get(Room, room.room_id)
        if db_room is not None:
            raise HTTPException(400, 'Room already exists')
        new_room = Room(creator=room.creator, room_id=room.room_id)
        # new_room = Room.from_orm(room)
        session.add(new_room)
        session.commit()
        session.refresh(new_room)
        return {'message': f'Room {room.room_id} created successfully'}


@router.delete('/room/{room_id}', status_code=200)
async def delete_room(room: RoomDelete):
    with Session(engine) as session:
        statement = select(Room).where(Room.room_id == room.room_id).where(Room.creator == room.username)
        db_room = session.exec(statement).first()
        user = session.exec(select(User).where(User.room_id == room.room_id)).first()
        if user:
            raise HTTPException(400, 'Unable to delete room with users in it')
        if not db_room:
            raise HTTPException(404, 'Room created by user not found')

        session.delete(db_room)
        session.commit()

        return {'message': 'Room deleted'}


@router.get('/rooms')
async def get_rooms():
    with Session(engine) as session:
        return session.exec(select(Room)).all()


@router.get('/room/{room_id}', response_model=Room)
async def get_room(room_id: int):
    with Session(engine) as session:
        return session.get(Room, room_id)


@router.post('/room/{room_id}/join')
async def join_room(room: RoomJoin):
    with Session(engine) as session:
        db_room = session.get(Room, room.room_id)
        db_user = session.get(User, room.username)

        if not db_room or not db_user:
            raise HTTPException(404, 'Room or user does not exist')
        if db_user.room_id:
            raise HTTPException(400, 'User already in a room.')

        db_user.room_id = db_room.room_id
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return {'message': f'User {room.username} joined room {room.room_id}'}


@router.post('/room/{room_id}/leave')
async def leave_room(room: RoomJoin):
    with Session(engine) as session:
        statement = select(User).where(User.username == room.username).where(User.room_id == room.room_id)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(404, 'User does not exist in that room, or room does not exist')

        user.room_id = None
        session.add(user)
        session.commit()
        session.refresh(user)

        return {'message': f'User {room.username} left room {room.room_id}'}
