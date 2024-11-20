import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from researchtikpy import get_liked_videos


@patch("requests.Session")
def test_get_liked_videos_success(mock_session):
    # Arrange
    liked_videos_data = {
        "data": {
            "user_liked_videos": [
                {"id": "12345", "video_description": "Video 1"},
                {"id": "67890", "video_description": "Video 2"},
            ],
            "has_more": False,
            "cursor": 0,
        }
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = liked_videos_data
    mock_session.return_value.post.return_value = mock_response
    usernames = ["testuser"]
    access_token = "test_access_token"

    # Act
    result_df = get_liked_videos(usernames, access_token, verbose=False)

    # Assert
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 2
    assert result_df.iloc[0]["id"] == "12345"


# TODO: This test causes the test suite to hang indefinitely, need to fix this.
# @patch('requests.Session')
# def test_get_liked_videos_rate_limit(mock_session):
#     # Arrange
#     mock_response = MagicMock()
#     mock_response.status_code = 429  # Simulate rate limit error from the API
#     mock_session.return_value.post.return_value = mock_response
#     usernames = ['testuser']
#     access_token = 'test_access_token'

#     # Act
#     result_df = get_liked_videos(usernames, access_token, verbose=False)

#     # Assert
#     assert result_df.empty

# Additional test cases can be added here to cover other scenarios.
