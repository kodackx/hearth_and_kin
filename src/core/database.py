from sqlmodel import SQLModel, create_engine, Session

import sys

# Use in-memory db for testing
sqlite_url = 'sqlite:///test.db' if 'pytest' in sys.modules else 'sqlite:///db/database.db'

connect_args = {'check_same_thread': False}

engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
