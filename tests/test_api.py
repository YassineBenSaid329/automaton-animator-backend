# tests/test_api.py

import pytest
from app import app as flask_app  # Import our main Flask app object


@pytest.fixture
def client():
    """
    A pytest fixture to create a test client for our Flask app.
    This allows us to send HTTP requests to the app in our tests.
    """
    with flask_app.test_client() as client:
        yield client


# --- Integration Tests ---

def test_api_valid_regex_returns_200_and_nfa(client):
    """
    Sends a valid regex to the live API endpoint and checks for a successful response.
    This is a full end-to-end "happy path" test.
    """
    # Define the request payload
    payload = {"regex": "a(b|c)*"}

    # Use the test client to send a POST request
    response = client.post("/api/regex-to-nfa", json=payload)

    # 1. Assert that the HTTP status code is 200 OK
    assert response.status_code == 200

    # 2. Assert that the response is valid JSON and contains the expected keys
    data = response.get_json()
    assert "states" in data
    assert "alphabet" in data
    assert "transitions" in data
    assert "start_state" in data
    assert "final_states" in data
    assert data["alphabet"] == ["a", "b", "c"]


def test_api_invalid_regex_returns_400_and_error_message(client):
    """
    Sends a grammatically incorrect regex to the API and checks for a 400 Bad Request error.
    This is a full end-to-end "sad path" test.
    """
    # Define the request payload with invalid syntax
    payload = {"regex": "a(b|"}

    # Use the test client to send a POST request
    response = client.post("/api/regex-to-nfa", json=payload)

    # 1. Assert that the HTTP status code is 400 Bad Request
    assert response.status_code == 400

    # 2. Assert that the response contains the correct JSON error message
    data = response.get_json()
    assert "error" in data
    assert "Unexpected end of expression, expecting an operand or '('" in data["error"]


def test_api_malformed_request_returns_400(client):
    """
    Sends a request with a missing 'regex' key to test the API's input validation.
    """
    # A payload that is missing the required "regex" key
    payload = {"wrong_key": "a"}

    response = client.post("/api/regex-to-nfa", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "'regex' key is missing" in data["error"]