import unittest
import researchtikpy

class TestResearchTikPy(unittest.TestCase):

    def test_version(self):
        self.assertEqual(researchtikpy.__version__, "0.2.1")

    def test_all_exports(self):
        expected_exports = [
            "AccessToken",
            "Condition",
            "Query",
            "get_following",
            "get_followers",
            "get_liked_videos",
            "get_pinned_videos",
            "get_users_info",
            "get_video_comments",
            "get_videos_hashtag",
            "get_videos_query",
            "get_videos_info",
        ]
        self.assertListEqual(sorted(researchtikpy.__all__), sorted(expected_exports))

if __name__ == '__main__':
    unittest.main()