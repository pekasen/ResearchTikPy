import os

from functools import cache
from unittest.mock import patch
from researchtikpy import AccessToken


@cache
@patch("requests.post")
def access_token(mock_post) -> str:
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": "test",
        "expires_in": 7200,
        "token_type": "Bearer",
    }

    data = AccessToken(
        client_key=os.environ[
            "TIKTOK_CLIENT_KEY"
        ],  # TODO: Do not run unit tests with real credentials
        client_secret=os.environ[
            "TIKTOK_CLIENT_SECRET"
        ],  # This is both unsafe and unnecessary - use mocks instead.
    )
    
    return data.token
