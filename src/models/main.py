from sqlmodel import SQLModel as Model, Field
from pydantic import validator
from bcrypt import hashpw, gensalt


class UserCreate(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)
    password: str = Field()

    @validator('password')
    def hash_password(cls, v):
        assert len(v) > 0, 'Password can\t be empty'
        if v[:8] == '__hash__':  # Avoid double-hashing when creating a User()
            return v
        return '__hash__' + hashpw(v.encode('utf-8'), gensalt()).decode('utf-8')


class UserLogin(UserCreate):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field()


class User(UserCreate, table=True):
    is_in_room: bool = Field(default=False, nullable=False)


class CreateGameRequest(Model):
    room_id: str = Field(min_length=1, max_length=20)


class NewStoryRequest(Model):
    keywords: str = Field(min_length=0, max_length=5000)


class MessageRequest(Model):
    message: str = Field(min_length=0, max_length=5000)
