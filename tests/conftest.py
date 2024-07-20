import asyncio
import pytest
from sqlalchemy import StaticPool
from sqlmodel import create_engine, Session, SQLModel
from src.main import app, get_session
from fastapi.testclient import TestClient
import multiprocessing
from uvicorn import Config, Server

from src.models.character import Character
from src.models.story import Story
from src.models.user import User


@pytest.fixture(name='session', scope='session')
def session_fixture():
    """
    Set up in-memory database for tests
    """
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name='client', scope='session')
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


class UvicornServer(multiprocessing.Process):

    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)
        self.config = config

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        self.server.run()

@pytest.fixture(scope="session")
def server():
    config = Config("src.main:app")
    instance = UvicornServer(config=config)
    instance.start()
    yield instance
    instance.stop()

@pytest.fixture
def chrome_options(chrome_options):
    #chrome_options.add_argument("--headless=new")
    return chrome_options

@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    return selenium

user_test_data = [
    {'username': 'user1', 'password': 'test'},
    {'username': 'user2', 'password': 'test'}
]

character_test_data = [
    {'description': 'desc','stat_cha': 5, 'character_name': 'character1'},
    {'description': 'desc','stat_cha': 5, 'character_name': 'character2'}
]

@pytest.fixture()
def users(client: TestClient, session: Session) -> list[User]:
    """Creates two users using the parameters of user_test_data in conftest.py
    """
    _users = []
    for user_data in user_test_data:

        response = client.post('/user', json=user_data)
        assert response.status_code == 201, 'User should be created successfully'

        _user = session.get(User, response.json()['user_id'])
        assert _user is not None
        _users.append(_user)

    return _users


@pytest.fixture()
def characters(client: TestClient, session: Session, users: list[User]) -> list[Character]:
    """"Creates characters for each user using the parameters of character_test_data in conftest.py
    """
    _characters = []
    for i,user in enumerate(users):
        character_data = character_test_data[i]
        character_data['user_id'] = user.user_id
        response = client.post('/createcharacter', json=character_data)
        
        assert response.status_code == 201, 'Character should be created successfully'
        _character = session.get(Character, response.json()['character_id'])
        assert _character is not None
        _characters.append(_character)
    
    return _characters

@pytest.fixture()
def stories(client: TestClient, session: Session, characters: list[Character]) -> list[Story]:
    """Creates two stories where the each character is the party lead
    """
    _stories = []
    for character in characters:
        response = client.post('/story', json={'party_lead': character.character_id})
        
        assert response.status_code == 201, 'Story should be created successfully'

        _story = session.get(Story, response.json()['story']['story_id'])
        assert _story is not None
        _stories.append(_story)
    return _stories