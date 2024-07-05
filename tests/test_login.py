import pytest
from sqlmodel import Session
from src.models.user import User, UserBase
from tests.conftest import default_user_data
from fastapi.testclient import TestClient
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
def test_login_model(user_input):
    with pytest.raises(ValidationError):
        UserBase.model_validate(user_input)


@pytest.mark.parametrize(
    'user_input, expected_status',
    [
        (default_user_data, 200), # Correct login
        ({'username': default_user_data['username'], 'password': 'wrong_pass'}, 401),
    ],
)
@pytest.mark.asyncio
async def test_login_logic(user_input, expected_status, client: TestClient, user: User):
    # Try logging in
    response = client.post('/login', data=user_input)
    assert response.status_code == expected_status, 'Logging in should return the expected status code'
