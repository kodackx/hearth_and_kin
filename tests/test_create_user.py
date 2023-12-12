import pytest
from src.main import app
from fastapi.testclient import TestClient
from src.models.user import User, UserCreate
from unittest.mock import patch
from src.api.user import create_user
from fastapi import Response
from pydantic.error_wrappers import ValidationError

client = TestClient(app)


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
    with pytest.raises(ValidationError):
        UserCreate(**user_input)


@pytest.mark.asyncio
async def test_create_user_logic_success():
    test_input = UserCreate(username='user', password='password')
    response = Response()

    with patch('src.api.user.Session') as mock_session:
        mock_enter = mock_session.return_value.__enter__.return_value
        mock_enter.get.return_value = None  # Simulate user not existing in the database
        mock_enter.add.return_value = None  # Simulate successful addition of user
        mock_enter.commit.return_value = None  # Simulate successful db commit
        mock_enter.refresh.return_value = None  # Simulate successful db refresh

        _ = await create_user(test_input, response)
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_user_logic_fail():
    test_input = UserCreate(username='user', password='password')
    response = Response()

    with patch('src.api.user.Session') as mock_session:
        mock_enter = mock_session.return_value.__enter__.return_value
        mock_enter.get.return_value = User(username='user', password='123')  # Simulate user existing in the database

        _ = await create_user(test_input, response)
        assert response.status_code == 400
