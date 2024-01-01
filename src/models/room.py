from sqlmodel import SQLModel as Model, Field


class RoomBase(Model):
    room_id: int = Field(nullable=False, primary_key=True)


class RoomUser(RoomBase):
    username: str = Field(foreign_key='user.username')


class RoomCreate(RoomUser):
    creator: str = Field(foreign_key='user.username', alias='username')


class Room(RoomCreate, table=True):
    pass
