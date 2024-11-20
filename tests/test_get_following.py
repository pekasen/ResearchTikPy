import pytest
from unittest.mock import patch, MagicMock
from researchtikpy import get_following
import pandas as pd


@patch("requests.Session")
def test_get_following_success(mock_session):
    # Arrange
    expected_following_data = {
        "data": {
            "user_following": [
                {"id": "1", "username": "following1"},
                {"id": "2", "username": "following2"},
            ],
            "has_more": False,
            "cursor": 0,
        }
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_following_data
    mock_session.return_value.post.return_value = mock_response
    usernames_list = ["testuser"]
    access_token = "test_access_token"

    # Act
    result_df = get_following(usernames_list, access_token, max_count=2, verbose=False)

    # Assert
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 2
    assert list(result_df["username"]) == ["following1", "following2"]


# TODO: This test causes the test suite to hang indefinitely, need to fix this.
# @patch('requests.Session')
# def test_get_following_rate_limit(mock_session):
#     # Arrange
#     mock_response = MagicMock()
#     mock_response.status_code = 429  # Simulate rate limit error from the API
#     mock_session.return_value.post.return_value = mock_response
#     usernames_list = ['testuser']
#     access_token = 'test_access_token'

#     # Act
#     result_df = get_following(usernames_list, access_token, verbose=False)

#     # Assert
#     assert result_df.empty

# Additional test cases can be added here to cover more scenarios.
