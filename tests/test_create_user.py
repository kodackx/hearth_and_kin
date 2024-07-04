import pytest
from src.models.user import User
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
        User.model_validate(user_input)


def test_create_user_logic_success(user: User):
    assert user is not None, 'User should be created successfully via the fixture in conftest.py'