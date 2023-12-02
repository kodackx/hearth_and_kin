from sqlmodel import SQLModel, create_engine, Session
from .config import DEBUG
from ..models.main import UserCreate, User
from typing import Optional

import sys

# Use in-memory db for testing
sqlite_url = 'sqlite://' if 'pytest' in sys.modules else 'sqlite:///db/database.db'

connect_args = {'check_same_thread': False}
# Only output SQL queries in debug mode
engine = create_engine(sqlite_url, echo=DEBUG, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def drop_tables():
    with Session(engine) as session:
        session.delete(User)


def get_users() -> list[User]:
    with Session(engine) as session:
        return session.get(User).all()


def get_user(username: str) -> Optional[User]:
    with Session(engine) as session:
        return session.get(User, username)


def create_user(user: UserCreate) -> None:
    new_user = User(**user.dict())
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
