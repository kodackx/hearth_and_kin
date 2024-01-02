from bcrypt import checkpw
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..core.database import get_session
from ..models.room import Room
from ..models.user import User, UserBase
from ..core.config import logger

router = APIRouter()


@router.post('/user', status_code=201)
async def create_user(*, user: UserBase, session: Session = Depends(get_session)):
    logger.debug(f'CREATE_USER: {user = }')

    db_user = session.get(User, user.username)
    if db_user is not None:
        raise HTTPException(400, 'Username already exists. Please try a different one.')
    new_user = User.from_orm(user)
    logger.debug(new_user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {'message': 'User registered successfully! Please log in now.'}


@router.get('/user/{username}/room')
async def get_user_room(*, session: Session = Depends(get_session), username: str):
    user = session.get(User, username)
    if user:
        return session.get(Room, user.room_id)
    raise HTTPException(status_code=404, detail='User not found')


@router.post('/login')
async def login(*, session: Session = Depends(get_session), user: UserBase):
    db_user = session.get(User, user.username)
    if db_user is not None and checkpw(user.password.encode(), db_user.password.encode()):
        return {'message': 'Login successful'}

    raise HTTPException(401, 'Invalid credentials')
