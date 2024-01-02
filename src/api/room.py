from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select


from ..models.user import User, UserRead
from ..core.database import get_session
from ..models.room import Room, RoomCreate, RoomJoin, RoomDelete

router = APIRouter()


@router.post('/room', status_code=201)
async def create_room(*, room: RoomCreate, session: Session = Depends(get_session)):
    db_room = session.get(Room, room.room_id)
    if db_room is not None:
        raise HTTPException(400, 'Room already exists')
    new_room = Room(creator=room.creator, room_id=room.room_id)

    session.add(new_room)
    session.commit()
    session.refresh(new_room)
    return {'message': f'Room {room.room_id} created successfully'}


@router.delete('/room/{room_id}', status_code=200)
async def delete_room(*, room: RoomDelete, session: Session = Depends(get_session)):
    statement = select(Room).where(Room.room_id == room.room_id).where(Room.creator == room.username)
    db_room = session.exec(statement).first()

    if not db_room:
        raise HTTPException(404, 'Room created by user not found')

    users = session.exec(select(User).where(User.room_id == room.room_id)).all()
    # Kick out any users in room
    for user in users:
        user.room_id = None
        session.add(user)

    session.delete(db_room)
    session.commit()

    return {'message': 'Room deleted'}


@router.get('/rooms')
async def get_rooms(session: Session = Depends(get_session)):
    return session.exec(select(Room)).all()


@router.get('/room/{room_id}', response_model=Room)
async def get_room(*, room_id: int, session: Session = Depends(get_session)):
    return session.get(Room, room_id)


@router.get('/room/{room_id}/users', response_model=list[UserRead])
async def get_room_users(*, session: Session = Depends(get_session), room_id: int):
    room = session.get(Room, room_id)
    if room:
        statement = select(User).where(User.room_id == room_id)
        return session.exec(statement).all()
    raise HTTPException(status_code=404, detail='Room not found')


@router.post('/room/{room_id}/join')
async def join_room(*, room: RoomJoin, session: Session = Depends(get_session)):
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
async def leave_room(*, room: RoomJoin, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == room.username).where(User.room_id == room.room_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(404, 'User does not exist in that room, or room does not exist')

    user.room_id = None
    session.add(user)
    session.commit()
    session.refresh(user)

    return {'message': f'User {room.username} left room {room.room_id}'}
