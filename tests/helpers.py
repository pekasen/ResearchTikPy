import os

from functools import cache
from researchtikpy import AccessToken


@cache
def access_token() -> str:
    data = AccessToken(
        client_key=os.environ["TIKTOK_CLIENT_KEY"],  # TODO: Do not run unit tests with real credentials
        client_secret=os.environ["TIKTOK_CLIENT_SECRET"],  # This is both unsafe and unnecessary - use mocks instead.
    )
    return data.token
