import pytest
from sqlalchemy import StaticPool
from sqlmodel import create_engine, Session, SQLModel
from src.main import app, get_session
from fastapi.testclient import TestClient


@pytest.fixture(name='session')
def session_fixture():
    """
    Set up in-memory database for tests
    """
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name='client')
def client_fixture(session: Session):
    """
    Set up app with in-memory database for tests
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
