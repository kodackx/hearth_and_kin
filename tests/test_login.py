import pytest
from sqlmodel import Session
from src.models.user import UserBase
from fastapi.testclient import TestClient
from pydantic import ValidationError
from tests.test_create_user import create_user, default_user_data

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
        (default_user_data, 200),
        ({'username': 'user', 'password': 'wrong_pass'}, 401),
    ],
)
@pytest.mark.asyncio
async def test_login_logic(user_input, expected_status, session: Session, client: TestClient):
    # Create the user first
    _ = create_user(client, session, default_user_data)
    # Try logging in
    response = client.post('/login', data=user_input)
    assert response.status_code == expected_status, 'Logging in should return the expected status code'
