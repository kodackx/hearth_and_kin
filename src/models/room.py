from sqlmodel import SQLModel as Model, Field


class RoomBase(Model):
    room_id: int = Field(nullable=False, primary_key=True)


class RoomJoin(RoomBase):
    username: str = Field(foreign_key='user.username')


class RoomCreate(RoomBase):
    creator: str = Field(foreign_key='user.username', alias='creator')


class RoomDelete(RoomJoin):
    pass


class RoomRead(RoomCreate):
    pass


class Room(RoomCreate, table=True):
    pass
