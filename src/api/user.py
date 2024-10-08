from bcrypt import checkpw, hashpw, gensalt
from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlmodel import Session, select

from ..core.database import get_session
from ..models.user import User, UserBase, UserRead, UserUpdate
from ..models.session import Token, LoginSession
from ..core.config import logger
from ..services.narrator import validate_api_key as narrator_validate_api_key
from ..services.audio import validate_api_key as audio_validate_api_key
from ..models.enums import AudioModel, TextModel
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os

router = APIRouter()

# Secret key to encode the JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def validate_api_key(model: AudioModel | TextModel, api_key: str) -> None:
    if model == AudioModel.elevenlabs and os.environ.get('TEST_ENV') != 'True':
        try:
            audio_validate_api_key(model, api_key)
        except Exception as e:
            logger.error(f'Error validating {model} API key: {e}')
            raise HTTPException(400, str(e))
    # TODO: add more models here, e.g. nvidia
    elif model in [TextModel.gpt] and os.environ.get('TEST_ENV') != 'True':
        try:
            narrator_validate_api_key(model, api_key)
        except Exception as e:
            logger.error(f'Error validating {model} API key: {e}')
            raise HTTPException(400, str(e))
                                  
@router.post('/user', status_code=201, response_model=UserRead)
async def create_user(*, user: UserBase, session: Session = Depends(get_session)):
    db_user = session.get(User, user.username)
    if db_user is not None:
        raise HTTPException(400, 'Username already exists. Please try a different one.')
    
    hashed_password = hashpw(user.password.encode('utf-8'), gensalt())
    user.password = hashed_password.decode('utf-8')
    new_user = User.model_validate(user)

    # Check that the API keys are valid
    if new_user.nvidia_api_key:
        validate_api_key(TextModel.nvidia, new_user.nvidia_api_key)
    
    if new_user.openai_api_key:
        validate_api_key(TextModel.gpt, new_user.openai_api_key)
    
    if new_user.elevenlabs_api_key:
        validate_api_key(AudioModel.elevenlabs, new_user.elevenlabs_api_key)

    logger.debug(f'CREATE_USER: {user = }')
    
    logger.debug(f'New user created: username={new_user.username}')
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post('/login', response_model=Token)
async def login(*, session: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    logger.debug(f'This is the username we will check for existance: {form_data.username}')
    # Fetch user by username
    statement = select(User).where(User.username == form_data.username)
    db_user = session.exec(statement).first()
    logger.debug(f'LOGIN: Retrieved user: {db_user}')
    if db_user:
        logger.debug(f'User found: {db_user.username}')
    else:
        logger.debug(f'User not found: {form_data.username}')
    # logger.debug(f'Will check encoded field: {form_data.password.encode('utf-8')} against stored password: {db_user.password.encode('utf-8')}')
    if db_user is None or not checkpw(form_data.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(data={"sub": db_user.username}, expires_delta=access_token_expires)
    return_payload = {"user_id": db_user.user_id, "access_token": access_token, "token_type": "bearer"}
    logger.debug(f'Return payload: {return_payload}')

    # Save login session details
    login_session = LoginSession(
        user_id=db_user.user_id,
        access_token=access_token,
        token_type="bearer"
    )
    session.add(login_session)
    session.commit()

    return return_payload

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

@router.patch('/user/{user_id}', status_code=201, response_model=UserRead)
async def update_user(*, user: UserUpdate, user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(404, 'User not found')
    user_data = user.model_dump(exclude_unset=True)
    
    for key, value in user_data.items():
        
        if key == 'password':
            hashed_password = hashpw(value.encode('utf-8'), gensalt())
            value = hashed_password.decode('utf-8')
        
        if key == 'elevenlabs_api_key':
            validate_api_key(AudioModel.elevenlabs, value)
        if key == 'nvidia_api_key':
            validate_api_key(TextModel.nvidia, value)
        if key == 'openai_api_key':
            validate_api_key(TextModel.gpt, value)
        
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    logger.debug(f'[USER]: updated user {db_user}')
    return db_user
