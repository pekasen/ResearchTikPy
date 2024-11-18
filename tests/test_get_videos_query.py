import unittest
from unittest.mock import patch

import pandas as pd
from pydantic import ValidationError
from researchtikpy import get_videos_query

access_token = "clt.SAMESYNTHETICDATATOKEN"
mock_json_response = {
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

class TestGetVideosQuery(unittest.TestCase):
    @patch('requests.post')
    def test_get_videos_query(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_json_response
        df = get_videos_query(
            query={"and": [{"operation": "IN", "field_name": "hashtag_name", "field_values": ["germany"]}]},
            access_token=access_token,
            start_date="20240101",
            end_date="20240102",
            total_max_count=10,
            max_count=10
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    @patch('requests.post')
    def test_invalid_query(self, mock_post):
        # 'operation' EQ must have one field value
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_json_response
        invalid_query = {"and": [{"operation": "EQ", "field_name": "keyword", "field_values": ["one", "two"]}]}
        with self.assertRaises(ValueError):
            get_videos_query(
                query=invalid_query,
                access_token=access_token,
                start_date="20240101",
                end_date="20240102",
                total_max_count=10,
                max_count=10
            )

