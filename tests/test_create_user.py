import pytest
from src.models.user import User
from pydantic import ValidationError
from tests.conftest import user_test_data

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