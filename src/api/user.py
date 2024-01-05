from bcrypt import checkpw
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.models.character import Character, CharacterRead
from ..core.database import get_session
from ..models.story import Story
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


@router.get('/user/{username}/story')
async def get_user_story(*, session: Session = Depends(get_session), username: str):
    user = session.get(User, username)
    if user:
        return session.get(Story, user.story_id)
    raise HTTPException(status_code=404, detail='User not found')


@router.post('/login')
async def login(*, session: Session = Depends(get_session), user: UserBase):
    db_user = session.get(User, user.username)
    if db_user is not None and checkpw(user.password.encode(), db_user.password.encode()):
        return {'message': 'Login successful'}

    raise HTTPException(401, 'Invalid credentials')


@router.get('/user/{username}/characters', status_code=200, response_model=list[CharacterRead])
async def get_characters(*, username: str, session: Session = Depends(get_session)):
    characters = session.exec(select(Character)).all()  # .where(Character.username == username)).all()
    if not characters:
        raise HTTPException(404, 'User not found')
    logger.debug(f'[USER]: returned {characters = }')
    return characters
