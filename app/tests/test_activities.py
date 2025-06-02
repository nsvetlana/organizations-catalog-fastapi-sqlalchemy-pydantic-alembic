import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"  # Используем SQLite для тестовой базы

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user
from app.db.base import Base
from app.db.session import engine  # Предполагается, что engine импортируется из app/db/session.py

# Фикстура, которая автоматически создаёт все таблицы перед запуском тестов
# и удаляет их после завершения сессии.
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Переопределяем зависимость для аутентификации, чтобы все запросы получали фиктивного пользователя.
def fake_get_current_user():
    return {"id": 1, "username": "testuser"}

app.dependency_overrides[get_current_user] = fake_get_current_user

client = TestClient(app)

def test_get_activities_empty():
    """
    Ensure GET /activities returns an empty list when no activities exist.
    """
    response = client.get("/activities/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_and_get_nested_activities():
    """
    Test creating nested activities up to the allowed depth (3 levels)
    and ensure that creating an activity beyond this depth fails.
    """
    # Создаем корневую активность.
    root_data = {"name": "Root Activity"}
    root_response = client.post("/activities/", json=root_data)
    assert root_response.status_code == 201
    root = root_response.json()
    root_id = root["id"]

    # Создание дочерней активности (Уровень 2)
    child_data = {"name": "Child Activity", "parent_id": root_id}
    child_response = client.post("/activities/", json=child_data)
    assert child_response.status_code == 201
    child = child_response.json()
    child_id = child["id"]

    # Создаем активность третьего уровня (Уровень 3)
    grandchild_data = {"name": "Grandchild Activity", "parent_id": child_id}
    grandchild_response = client.post("/activities/", json=grandchild_data)
    assert grandchild_response.status_code == 201
    grandchild = grandchild_response.json()

    # Попытка создать активность четвертого уровня (Уровень 4) должна привести к ошибке.
    great_grandchild_data = {"name": "Great-Grandchild Activity", "parent_id": grandchild["id"]}
    great_grandchild_response = client.post("/activities/", json=great_grandchild_data)
    assert great_grandchild_response.status_code == 400
    detail = great_grandchild_response.json().get("detail", "")
    assert "Maximum nesting level of 3 exceeded" in detail
