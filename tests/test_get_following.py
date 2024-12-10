from json import JSONDecodeError
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


@patch("requests.Session")
def test_get_following_JSONDecodeError(mock_session):
    """Should retry the current request on JSONDecodeError."""
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
    _call_count_ = 0
    def raise_on_first_call(*args, **kwargs):
        nonlocal _call_count_
        if _call_count_ == 0:
            _call_count_ += 1
            print("JSONDecodeError occurred. Retrying the request.")
            raise JSONDecodeError("Invalid JSON data", "", 0)
        else:
            print("Retrying the request was succesful.")
            return expected_following_data
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = raise_on_first_call
    mock_session.return_value.post.return_value = mock_response
    usernames_list = ["testuser"]
    access_token = "test_access_token"

    # Act
    result_df = get_following(usernames_list, access_token, max_count=2, verbose=False)

    # Assert
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 2
    assert list(result_df["username"]) == ["following1", "following2"]
    assert False


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
