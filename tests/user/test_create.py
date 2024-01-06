import pytest
from src.models.user import UserBase
from fastapi.testclient import TestClient
from sqlmodel import Session
from pydantic import ValidationError


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
    response = client.post('/user', json={'username': 'test', 'password': 'test'})
    assert response.status_code == 201  # Valid user info


@pytest.mark.asyncio
async def test_create_user_logic_fail(session: Session, client: TestClient):
    response = client.post('/user', json={'username': 'test', 'password': 'test'})
    assert response.status_code == 201  # Valid user info
    response = client.post('/user', json={'username': 'test', 'password': 'test'})
    assert response.status_code == 400  # Cant create two users with same username
