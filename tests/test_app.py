import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code in [200, 307]  # Both status codes are acceptable for redirects
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    # Verify activity structure
    activity = activities["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up test@mergington.edu for Chess Club"

    # Verify the student was actually added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    # First signup
    client.post(
        "/activities/Programming Class/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    
    # Try to signup again
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_signup_nonexistent_activity():
    response = client.post(
        "/activities/NonexistentClub/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"