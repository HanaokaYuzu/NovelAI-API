import asyncio
import unittest
from unittest.mock import MagicMock, patch

from novelai import NAIClient, APIError, AuthError, NovelAIError, HOSTS, ENDPOINTS


class TestInit(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.naiclient = NAIClient("test_username", "test_password")

    @patch("novelai.client.AsyncClient.post")
    @patch("novelai.client.encode_access_key")
    async def test_success(self, mock_encode_access_key, mock_post):
        # Mocks
        mock_encode_access_key.return_value = "test_key"
        mock_post.return_value.status_code = 201
        mock_post.return_value.json = MagicMock(
            return_value={"accessToken": "test_token"}
        )

        # Function call
        await self.naiclient.init(timeout=33, auto_close=True, close_delay=0)

        # Assertions
        self.assertEqual(self.naiclient.client.timeout.connect, 33)
        self.assertEqual(self.naiclient.auto_close, True)
        self.assertEqual(self.naiclient.close_delay, 0)
        self.assertEqual(
            self.naiclient.client.headers["Authorization"], "Bearer test_token"
        )
        self.assertTrue(self.naiclient.running)
        mock_post.assert_called_once_with(
            url=f"{HOSTS.API.url}{ENDPOINTS.LOGIN}",
            json={"key": "test_key"},
        )

        # Awaited tasks assertions
        await asyncio.sleep(0.01)
        self.assertFalse(self.naiclient.running)

    @patch("novelai.client.AsyncClient.post")
    async def test_exceptions(self, mock_post):
        # Error cases
        error_codes = [400, 401, 500]
        exceptions = [APIError, AuthError, NovelAIError]

        for code, exception in zip(error_codes, exceptions):
            with self.subTest(f"Status code: {code}"):
                mock_post.return_value.status_code = code

                # Assert exception is raised
                with self.assertRaises(exception):
                    await self.naiclient.init(auto_close=False)

                # Assert AsyncClient is created but closed
                self.assertTrue(self.naiclient.client.is_closed)
                self.assertFalse(self.naiclient.running)


if __name__ == "__main__":
    unittest.main()
