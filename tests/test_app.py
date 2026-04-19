import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)


def test_root_redirect(client):
    """Test GET / redirects to static index.html"""
    # Arrange: No setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test GET /activities returns all activities"""
    # Arrange: No setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity = "Chess Club"
    email = "newstudent@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity}"

    # Verify added to participants
    resp = client.get("/activities")
    activities = resp.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate(client):
    """Test signup fails when student already signed up"""
    # Arrange
    activity = "Chess Club"
    email = "duplicatestudent@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")  # First signup

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_activity_not_found(client):
    """Test signup fails for non-existent activity"""
    # Arrange: No setup needed

    # Act
    response = client.post("/activities/NonExistentActivity/signup?email=test@example.com")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_participant_success(client):
    """Test successful removal of a participant"""
    # Arrange
    activity = "Programming Class"
    email = "removeme@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")  # Add first

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Removed {email} from {activity}"

    # Verify removed
    resp = client.get("/activities")
    activities = resp.json()
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found(client):
    """Test removal fails when participant not in activity"""
    # Arrange: No setup needed

    # Act
    response = client.delete("/activities/Chess Club/participants/notsignedup@example.com")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_remove_participant_activity_not_found(client):
    """Test removal fails for non-existent activity"""
    # Arrange: No setup needed

    # Act
    response = client.delete("/activities/NonExistentActivity/participants/test@example.com")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]