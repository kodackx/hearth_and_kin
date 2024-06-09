from bcrypt import checkpw, hashpw, gensalt
from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlmodel import Session
from ..core.database import get_session
from ..models.user import User, UserBase, UserRead
from ..core.config import logger
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import os

router = APIRouter()

# Secret key to encode the JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post('/user', status_code=201, response_model=UserRead)
async def create_user(*, user: UserBase, session: Session = Depends(get_session)):
    logger.debug(f'CREATE_USER: {user = }')

    db_user = session.get(User, user.username)
    if db_user is not None:
        raise HTTPException(400, 'Username already exists. Please try a different one.')
    
    hashed_password = hashpw(user.password.encode(), gensalt())
    new_user = User.model_validate(user)
    new_user.password = hashed_password.decode()
    
    logger.debug(new_user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post('/login', response_model=Token)
async def login(*, session: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = session.get(User, form_data.username)
    if db_user is None or not checkpw(form_data.password.encode(), db_user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.user_id}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = session.get(User, username)
    if user is None:
        raise credentials_exception
    return user

@router.get('/protected-route', response_model=UserRead)
async def protected_route(current_user: User = Security(get_current_user)):
    return current_user