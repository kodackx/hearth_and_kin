import pytest
from typing import Generator
from src.models.user import UserRead, UserBase
from fastapi.testclient import TestClient
from sqlmodel import Session
from pydantic import ValidationError

default_user_data = {'username': 'test', 'password': 'test'}


def create_user(client: TestClient, session: Session, user_data: dict | None = None) -> UserRead:
    response = client.post('/user', json=user_data or default_user_data)
    assert response.status_code == 201  # Valid user info
    user = response.json()
    return UserRead.model_validate(user)

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
        UserBase.model_validate(user_input)


@pytest.mark.asyncio
async def test_create_user_logic_success(session: Session, client: TestClient):
    user = create_user(client, session)

    assert user.username == default_user_data['username'], 'User should be created with the requested username'
