from sqlmodel import SQLModel as Model, Field, Relationship


class RoomBase(Model):
    room_id: int = Field(nullable=False, primary_key=True)


class RoomUser(RoomBase):
    username: str


class RoomCreate(RoomUser):
    pass


class RoomRead(RoomCreate):
    users: list['User'] = Relationship(back_populates='room')  # noqa: F821


class Room(RoomRead, table=True):
    pass
