from bcrypt import checkpw
from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import Session
from src.core.database import engine
from src.models.user import User, UserBase
from src.core.config import logger

router = APIRouter()


@router.post('/user')
async def create_user(user: UserBase, response: Response):
    logger.debug(f'CREATE_USER: {user = }')
    with Session(engine) as session:
        db_user = session.get(User, user.username)
        if db_user is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'error': 'Username already exists. Please try a different one.'}
        new_user = User.from_orm(user)
        logger.debug(new_user)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        response.status_code = status.HTTP_201_CREATED
        return {'message': 'User registered successfully! Please log in now.'}


@router.get('/user/{username}/room')
async def get_user_room(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        return user.room_id


@router.post('/login')
async def login(user: UserBase, response: Response):
    with Session(engine) as session:
        db_user = session.get(User, user.username)
        if db_user is not None and checkpw(user.password.encode(), db_user.password.encode()):
            response.status_code = status.HTTP_200_OK
            return {'message': 'Login successful'}

        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'error': 'Invalid credentials'}
