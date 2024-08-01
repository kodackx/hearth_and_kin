import pytest
from src.datamodels.user import User
from pydantic import ValidationError
from tests.conftest import user_test_data
from fastapi.testclient import TestClient
from sqlmodel import Session


@pytest.mark.parametrize(
    'user_input',
    [
        ({'username': 'user', 'password': ''}),
        ({'username': '', 'password': ''}),
        ({'username': 'user'}),
        ({'password': 'pass'}),
    ],
)
def test_create_user_model(user_input):
    # Cant create user with too short username or password
    with pytest.raises(ValidationError):
        User.model_validate(user_input)


def test_create_user(users: list[User]):
    for i, user in enumerate(users):
        assert user.username == user_test_data[i]['username'], 'User should be created with the requested username'

def test_update_user_api_key(client: TestClient, session: Session, users: list[User]):
    user1 = users[0]

    data = {
        'user_id': user1.user_id,
        'openai_api_key': 'mock',
    }

    # Update user1
    response = client.patch(f'/user/{user1.user_id}', json=data)

    # Verify user updated
    assert response.status_code == 201, f'{response.json()}'#'User should be updated successfully'
    db_user = session.get(User, user1.user_id)
    assert db_user is not None

    assert db_user.openai_api_key == data['openai_api_key'], 'User should have updated openai_api_key'


def test_update_user_password(client: TestClient, session: Session, users: list[User]):
    user1 = users[0]
    old_password = session.get(User, user1.user_id).password

    data = {
        'user_id': user1.user_id,
        'password': 'new_pass',
    }

    # Update user1
    response = client.patch(f'/user/{user1.user_id}', json=data)

    # Verify user updated
    assert response.status_code == 201, 'User should be updated successfully'
    new_db_user = session.get(User, user1.user_id)
    assert new_db_user is not None

    assert old_password != new_db_user.password, 'User password should be updated'
    assert new_db_user.password != data['password'], 'User password should be hashed'

