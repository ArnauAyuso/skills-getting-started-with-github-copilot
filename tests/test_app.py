import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test cases for activities endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Check that required fields are present
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_signup_already_registered(self):
        """Test signup when student is already registered"""
        email = "duplicate@mergington.edu"
        activity = "Programming%20Class"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"]

    def test_unregister_from_activity_success(self):
        """Test successful unregistration from an activity"""
        email = "unregister@mergington.edu"
        activity = "Tennis%20Club"
        
        # First sign up
        client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "Unregistered" in result["message"]

    def test_unregister_nonexistent_activity(self):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_not_registered(self):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        result = response.json()
        assert "not registered" in result["detail"]

    def test_participant_count_changes_on_signup(self):
        """Test that participant count increases on signup"""
        # Get initial state
        response1 = client.get("/activities")
        activities1 = response1.json()
        initial_count = len(activities1["Basketball Team"]["participants"])
        
        # Sign up
        email = "basketball@mergington.edu"
        client.post(
            "/activities/Basketball%20Team/signup?email=" + email
        )
        
        # Get updated state
        response2 = client.get("/activities")
        activities2 = response2.json()
        updated_count = len(activities2["Basketball Team"]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in activities2["Basketball Team"]["participants"]

    def test_participant_removed_on_unregister(self):
        """Test that participant is removed on unregister"""
        email = "remove@mergington.edu"
        activity = "Drama%20Club"
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Verify they are registered
        response1 = client.get("/activities")
        activities1 = response1.json()
        assert email in activities1["Drama Club"]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Verify they are removed
        response2 = client.get("/activities")
        activities2 = response2.json()
        assert email not in activities2["Drama Club"]["participants"]
