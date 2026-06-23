from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Backup and restore the in-memory `activities` between tests."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirect():
    # Arrange
    # Act
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert email in response.json()["message"]


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = "duplicate@mergington.edu"
    activities[activity]["participants"].append(email)

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400


def test_signup_activity_not_found():
    # Arrange
    activity = "Nonexistent"
    email = "x@x.com"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_success():
    # Arrange
    activity = "Chess Club"
    email = "toremove@mergington.edu"
    activities[activity]["participants"].append(email)
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_participant_not_found():
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 400


def test_unregister_activity_not_found():
    # Arrange
    activity = "NoActivity"
    email = "x@x.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
