from sqlmodel import SQLModel as Model, Field, Relationship


class RoomBase(Model):
    room_id: int = Field(nullable=False, primary_key=True)


class RoomCreate(RoomBase):
    pass


class RoomRead(RoomBase):
    users: list['User'] = Relationship(back_populates='room')  # noqa: F821


class Room(RoomRead, table=True):
    pass
