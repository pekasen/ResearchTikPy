import time
import pytest
from unittest.mock import patch
from researchtikpy import AccessToken


@patch("requests.post")
def test_token_retrieval_success(mock_post):
    # Arrange
    expected_response = {
        "access_token": "test_access_token",
        "expires_in": 7200,
        "token_type": "Bearer",
    }
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = expected_response
    client_key = "test_client_key"
    client_secret = "test_client_secret"

    # Act
    access_token = AccessToken(client_key, client_secret)
    response = {
        "access_token": access_token.token,
        "expires_in": 7200,
        "token_type": "Bearer",
    }

    # Assert
    assert response == expected_response


@patch("requests.post")
def test_token_retrieval_failure(mock_post):
    # Arrange
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"
    client_key = "test_client_key"
    client_secret = "test_client_secret"

    # Act & Assert
    with pytest.raises(Exception) as context:
        AccessToken(client_key, client_secret)

    assert "Failed to obtain access token" in str(context.value)


@patch("requests.post")
def test_token_retrieval_error(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "error": "invalid_client",
        "error_description": "Invalid client",
    }

    with pytest.raises(Exception):
        AccessToken("test_client_key", "test_client_secret")


@patch("requests.post")
def test_token_retrieval_none(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": None,
        "expires_in": 7200,
        "token_type": "Bearer",
    }

    with pytest.raises(Exception):
        AccessToken("test_client_key", "test_client_secret")


@patch("requests.post")
def test_access_token_automatic_refresh(mock_post):
    # Arrange
    expected_response = {
        "access_token": "test_access_token_2",
        "expires_in": 7200,
        "token_type": "Bearer",
    }
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": "test_access_token_1",
        "expires_in": 0.125,  # expires in a quarter of a second
        "token_type": "Bearer",
    }
    client_key = "test_client_key"
    client_secret = "test_client_secret"

    # Act
    access_token = AccessToken(client_key, client_secret)
    time.sleep(0.5)  # wait for the token to expire
    mock_post.return_value.json.return_value = expected_response
    response = {
        "access_token": access_token.token,
        "expires_in": 7200,
        "token_type": "Bearer",
    }
    # Assert
    assert response == expected_response


@patch("requests.post")
def test_access_token_str(mock_post):
    # Arrange
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": "test_access_token",
        "expires_in": 7200,
        "token_type": "Bearer",
    }
    client_key = "test_client_key"
    client_secret = "test_client_secret"

    # Act
    access_token = AccessToken(client_key, client_secret)
    response = str(access_token)

    # Assert
    assert (
        response
        == f"Bearer: {access_token.token}, expires at: {access_token.expires_at}"
    )
