from fastapi.testclient import TestClient
import pytest
import asyncio
from tests.conftest import user_test_data
from selenium.webdriver.common.by import By
from selenium.webdriver.support.events import EventFiringWebDriver

from src.models.user import User  


@pytest.mark.asyncio
async def test_login_flow(server, selenium: EventFiringWebDriver, users: list[User], client, session):
    user1, user2 = users
    await asyncio.sleep(1)
    selenium.get("http://127.0.0.1:8000/")
    selenium.find_element(By.ID, "username").send_keys(user1.username)
    selenium.find_element(By.ID, "password").send_keys(user_test_data[0]['password'])
    selenium.find_element(By.ID, "loginBtn").click()
    await asyncio.sleep(1)
    assert selenium.current_url == 'http://127.0.0.1:8000/dashboard', "Successful login redirects to dashboard"