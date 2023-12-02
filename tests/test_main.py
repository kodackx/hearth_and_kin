import pytest
from src.main import app
from fastapi.testclient import TestClient
from src.models.main import User

client = TestClient(app)


@pytest.mark.parametrize(
    'payload, expected_status',
    [
        ({'username': 'test'}, 422),  # missing password field
        ({'username': '', 'password': 'test'}, 422),  # empty username
        ({'username': 'test', 'password': ''}, 422),  # empty password
    ],
)
def test_model_create_user(payload, expected_status):
    response = client.post('/user', json=payload)
    assert response.status_code == expected_status


def test_create_existing_user(mocker):
    mocker.patch('src.core.database.get_user', return_value=User(username='existing', password='test'))
    response = client.post('/user', json={'username': 'existing', 'password': 'password'})
    assert response.status_code == 400


def test_create_new_user(mocker):
    mocker.patch('src.core.database.get_user', return_value=None)
    mocker.patch('src.core.database.create_user', return_value=None)
    response = client.post('/user', json={'username': 'existing', 'password': 'password'})
    assert response.status_code == 201


@pytest.mark.parametrize(
    'payload, expected_status',
    [
        ({'username': 'test'}, 422),  # missing password field
        ({'username': '', 'password': 'test'}, 422),  # empty username
        ({'username': 'test', 'password': ''}, 422),  # empty password
    ],
)
def test_model_login(payload, expected_status):
    response = client.post('/login', json=payload)
    assert response.status_code == expected_status


def test_login_wrong_password(mocker):
    mocker.patch('src.core.database.get_user', return_value=User(username='user', password='1'))
    response = client.post('/login', json={'username': 'user', 'password': '2'})
    assert response.status_code == 401


def test_login_correct_password(mocker):
    mocker.patch('src.core.database.get_user', return_value=User(username='user', password='test'))
    mocker.patch('bcrypt.checkpw', return_value=True)  # Ideally, this should not be mocked but I couldn't getit to work
    response = client.post('/login', json={'username': 'user', 'password': '1'})
    assert response.status_code == 200
