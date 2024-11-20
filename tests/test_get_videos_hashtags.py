import pytest
from unittest.mock import patch
import pandas as pd
from researchtikpy import get_videos_hashtag
from .helpers import access_token


@patch("requests.post")
def test_get_videos_hashtag(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "data": {
            "videos": [
                {
                    "id": "123456789",
                    "video_id": "123456789",
                    "hashtag_name": "germany",
                    "user_id": "123456789",
                    "user_name": "test_user",
                    "user_avatar": "https://test.com/avatar.jpg",
                    "video_url": "https://test.com/video.mp4",
                    "video_thumbnail": "https://test.com/thumbnail.jpg",
                    "video_title": "test_title",
                    "video_description": "test_description",
                    "video_duration": 60,
                    "video_views": 1000,
                    "video_likes": 100,
                    "video_comments": 10,
                    "video_shares": 5,
                    "video_timestamp": "20240101",
                    "video_hashtags": ["germany"],
                    "video_music": "test_music",
                    "video_effect": "test_effect",
                    "video_cover": "https://test.com/cover.jpg",
                    "video_original": "https://test.com/original.mp4",
                    "video_download": "https://test.com/download.mp4",
                    "video_stitched": "https://test.com/stitched.mp4",
                    "video_duet": "https://test.com/duet.mp4",
                }
            ]
        }
    }
    token = "clt.SAMESYNTHETICDATATOKEN"
    df = get_videos_hashtag(
        hashtags=["germany"],
        access_token=token,
        start_date="20240101",
        end_date="20240102",
        total_max_count=10,
        max_count=10,
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
