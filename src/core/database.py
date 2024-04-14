from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
import urllib
from src.core.storage import get_secret

sqlite_url = 'sqlite:///db/database.db'

connect_args = {'check_same_thread': False}

engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

username = get_secret('db-test-admin-username')
password = get_secret('db-test-admin-password')
params = urllib.parse.quote_plus(r'Driver={ODBC Driver 18 for SQL Server};Server=tcp:hearthandkin-test.database.windows.net,1433;Database=test;Uid=' + username + ';Pwd=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine_azure = create_engine(conn_str,echo=False, connect_args=connect_args)


with engine_azure.connect() as connection:
    # Run the SELECT 1 query
    result = connection.execute(text("SELECT 1;"))
    # Fetch the result
    row = result.fetchone()
    # Print the result
    print(row[0])