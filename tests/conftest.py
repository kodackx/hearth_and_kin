import pytest
from sqlalchemy import StaticPool
from sqlmodel import create_engine, Session, SQLModel
from src.main import app, get_session
from fastapi.testclient import TestClient

from src.models.character import Character, CharacterRead
from src.models.story import Story
from src.models.user import User, UserRead


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



default_user_data = {'username': 'test', 'password': 'test'}

@pytest.fixture()
def user(client: TestClient, session: Session, user_data: dict | None = None) -> User:

    user_data = user_data or {}

    # Create user with requested or default data
    for key, value in default_user_data.items():
        if key not in user_data:
            user_data[key] = value
    response = client.post('/user', json=user_data)
    assert response.status_code == 201, 'User should be created successfully'

    _user = session.get(User, response.json()['user_id'])
    assert _user is not None
    assert _user.username == user_data['username'], 'User should be created with the requested username'

    return _user

@pytest.fixture()
def user2(client: TestClient, session: Session) -> User:
    response = client.post('/user', json={'username': 'test2', 'password': 'test'})
    _user = session.get(User, response.json()['user_id'])
    assert _user is not None
    return _user

default_character_data = {'description': 'desc','stat_cha': 5, 'character_name': 'test_character'}

@pytest.fixture()
def character(client: TestClient, session: Session, user: User, character_data: dict | None = None) -> Character:
    character_data = character_data or {}
    
    # Create character with requested or default data
    for key, value in default_character_data.items():
        if key not in character_data:
            character_data[key] = value
    character_data['user_id'] = user.user_id
    response = client.post('/createcharacter', json=character_data)
    assert response.status_code == 201, 'Character should be created successfully'

    _character = session.get(Character, response.json()['character_id'])
    
    assert _character is not None
    assert _character.description == character_data['description'], 'Character should be created with the requested description'
    assert _character.character_name == character_data['character_name'], 'Character should be created with the requested name'
    
    return _character

@pytest.fixture()
def character2(client: TestClient, session: Session, user2: User, character_data: dict | None = None) -> Character:
    response = client.post('/createcharacter', json={'description': 'desc','stat_cha': 5, 'character_name': 'test_character2', 'user_id': user2.user_id})
    _character = session.get(Character, response.json()['character_id'])
    assert _character is not None
    return _character


@pytest.fixture()
def story(client: TestClient, session: Session, character: Character, story_data: dict | None = None) -> Story:
    # Create story
    story_data = story_data or {}
    story_data['party_lead'] = character.character_id
    
    response = client.post('/story', json=story_data)
    
    assert response.status_code == 201, 'Story should be created successfully'
    story = response.json()
    story = session.get(Story, story['story']['story_id'])
    assert story is not None
    return story