import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def reset_activities():
    # reset the in-memory activities to initial sample data for test isolation
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    })


@pytest.fixture(autouse=True)
def run_around_tests():
    # Reset activities before each test
    reset_activities()
    yield
    reset_activities()


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_and_duplicate():
    res = client.post("/activities/Chess Club/signup?email=test.student@mergington.edu")
    assert res.status_code == 200
    assert "Signed up test.student@mergington.edu" in res.json()["message"]

    # signing again should fail
    res2 = client.post("/activities/Chess Club/signup?email=test.student@mergington.edu")
    assert res2.status_code == 400


def test_remove_participant():
    # existing participant
    res = client.delete("/activities/Chess Club/participants?email=michael@mergington.edu")
    assert res.status_code == 200
    assert "Removed michael@mergington.edu" in res.json()["message"]

    # ensure participant removed
    data = client.get("/activities").json()
    assert "michael@mergington.edu" not in data["Chess Club"]["participants"]


def test_remove_nonexistent():
    res = client.delete("/activities/Chess Club/participants?email=not@here.com")
    assert res.status_code == 404
