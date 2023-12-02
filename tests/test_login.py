import pytest
from src.main import app
from fastapi.testclient import TestClient
from src.models.user import User, UserBase
from unittest.mock import patch
from src.api.user import login
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
def test_login_model(user_input):
    with pytest.raises(ValidationError):
        UserBase(**user_input)


@pytest.mark.parametrize(
    'user_input, expected_status',
    [
        ({'username': 'user', 'password': 'pass'}, 200),
        ({'username': 'user', 'password': 'wrong_pass'}, 401),
    ],
)
@pytest.mark.asyncio
async def test_login_logic(user_input, expected_status):
    test_input = UserBase(**user_input)
    mock_db_response = User(username='user', password='pass')
    response = Response()

    with patch('src.api.user.Session') as mock_db:
        mock_db.return_value.__enter__.return_value.get.return_value = mock_db_response
        _ = await login(test_input, response)
        assert response.status_code == expected_status
