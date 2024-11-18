import time
import unittest
from unittest.mock import patch
from researchtikpy import AccessToken

class TestGetAccessToken(unittest.TestCase):

    @patch('requests.post')
    def test_token_retrieval_success(self, mock_post):
        # Arrange
        expected_response = {
            "access_token": "test_access_token",
            "expires_in": 7200,
            "token_type": "Bearer"
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response
        client_key = 'test_client_key'
        client_secret = 'test_client_secret'

        # Act
        access_token = AccessToken(client_key, client_secret)
        response = {
            "access_token": access_token.token,
            "expires_in": 7200,
            "token_type": "Bearer"
        }

        # Assert
        self.assertEqual(response, expected_response)

    @patch('requests.post')
    def test_token_retrieval_failure(self, mock_post):
        # Arrange
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = 'Bad Request'
        client_key = 'test_client_key'
        client_secret = 'test_client_secret'

        # Act & Assert
        with self.assertRaises(Exception) as context:
            AccessToken(client_key, client_secret)
        
        self.assertIn('Failed to obtain access token', str(context.exception))


    @patch('requests.post')
    def test_token_retrieval_error(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "error": "invalid_client",
            "error_description": "Invalid client"
        }

        with self.assertRaises(Exception):
            AccessToken('test_client_key', 'test_client_secret')

    @patch('requests.post')
    def test_token_retrieval_none(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": None,
            "expires_in": 7200,
            "token_type": "Bearer"
        }

        with self.assertRaises(Exception):
            AccessToken('test_client_key', 'test_client_secret')

    @patch('requests.post')
    def test_access_token_automatic_refresh(self, mock_post):
        # Arrange
        expected_response =  {
            "access_token": "test_access_token_2",
            "expires_in": 7200,
            "token_type": "Bearer"
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "test_access_token_1",
            "expires_in": 0.125,  # expires in a quarter of a second
            "token_type": "Bearer"
        }
        client_key = 'test_client_key'
        client_secret = 'test_client_secret'

        # Act
        access_token = AccessToken(client_key, client_secret)
        time.sleep(0.5)  # wait for the token to expire
        mock_post.return_value.json.return_value = expected_response
        response = {
            "access_token": access_token.token,
            "expires_in": 7200,
            "token_type": "Bearer"
        }
        # Assert
        self.assertEqual(response, expected_response)

    @patch('requests.post')
    def test_access_token_str(self, mock_post):
        # Arrange
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "test_access_token",
            "expires_in": 7200,
            "token_type": "Bearer"
        }
        client_key = 'test_client_key'
        client_secret = 'test_client_secret'

        # Act
        access_token = AccessToken(client_key, client_secret)
        response = str(access_token)

        # Assert
        self.assertEqual(response, f"Bearer: {access_token.token}, expires at: {access_token.expires_at}")

if __name__ == '__main__':
    unittest.main()
