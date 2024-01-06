from bcrypt import checkpw
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..core.database import get_session
from ..models.user import User, UserBase, UserRead
from ..core.config import logger

router = APIRouter()


@router.post('/user', status_code=201, response_model=UserRead)
async def create_user(*, user: UserBase, session: Session = Depends(get_session)):
    logger.debug(f'CREATE_USER: {user = }')

    db_user = session.get(User, user.username)
    if db_user is not None:
        raise HTTPException(400, 'Username already exists. Please try a different one.')
    new_user = User.model_validate(user)
    logger.debug(new_user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post('/login', response_model=UserRead)
async def login(*, session: Session = Depends(get_session), user: UserBase):
    db_user = session.get(User, user.username)
    if db_user is not None and checkpw(user.password.encode(), db_user.password.encode()):
        return db_user

    raise HTTPException(401, 'Invalid credentials')
