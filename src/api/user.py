from fastapi import APIRouter, Response, status
from ..core.database import Session, engine
from ..models.user import UserCreate, User, UserLogin
from ..core.config import logger

router = APIRouter()


@router.post('/user')
async def create_user(user: UserCreate, response: Response):
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


@router.post('/login')
async def login(user: UserLogin, response: Response):
    with Session(engine) as session:
        db_user = session.get(User, user.username)
        print(user.password.encode()[8:], db_user.password.encode()[8:])
        if (
            db_user is not None and user.password == db_user.password
        ):  # checkpw(user.password.encode()[8:], db_user.password.encode()[8:]):
            response.status_code = status.HTTP_200_OK
            return {'message': 'Login successful'}

        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'error': 'Invalid credentials'}
