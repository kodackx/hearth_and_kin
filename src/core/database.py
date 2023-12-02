from sqlmodel import SQLModel, create_engine
from src.core.config import DEBUG


sqlite_url = "sqlite://db/database.db"

connect_args = {"check_same_thread": False}
# Only output SQL queries in debug mode
engine = create_engine(sqlite_url, echo=DEBUG, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)