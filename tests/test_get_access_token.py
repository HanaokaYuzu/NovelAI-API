import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient

from novelai import (
    NAIClient,
    APIError,
    AuthError,
    NovelAIError,
    HOSTS,
    ENDPOINTS,
    HEADERS,
)


class TestGetAccessToken(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.naiclient = NAIClient(
            os.getenv("USERNAME") or "test_username",
            os.getenv("PASSWORD") or "test_password",
        )
        self.naiclient.client = AsyncClient(headers=HEADERS)

    @unittest.skipIf(
        not (os.getenv("USERNAME") and os.getenv("PASSWORD")),
        "Skipping test_success...",
    )
    async def test_success(self):
        # Function call
        output_token = await self.naiclient.get_access_token()

        # Send testing request to NovelAI's API
        self.naiclient.client.headers["Authorization"] = f"Bearer {output_token}"
        response = await self.naiclient.client.get(
            url=f"{HOSTS.API.url}{ENDPOINTS.USERDATA}"
        )

        # Assertions
        self.assertEqual(response.status_code, 200)

    @patch("novelai.client.NAIClient.user")
    async def test_auth_error(self, mock_user):
        # Mock the user object to return wrong username and password
        mock_user.return_value = MagicMock(
            username="wrong_username", password="wrong_password"
        )

        # Function call & assertion
        with self.assertRaises(AuthError) as context:
            await self.naiclient.get_access_token()
        self.assertEqual(str(context.exception), "Invalid username or password.")

    @patch("novelai.client.encode_access_key")
    async def test_validation_error(self, mock_encode_access_key):
        # Mock the encode_access_key function to return a wrong string
        mock_encode_access_key.return_value = "misformatted_string"

        # Function call & assertion
        with self.assertRaises(APIError) as context:
            await self.naiclient.get_access_token()
        self.assertEqual(str(context.exception), "A validation error occured.")

    async def test_exceptions(self):
        # Error cases
        error_codes = [400, 401, 500]
        error_exceptions = [APIError, AuthError, NovelAIError]

        for code, exception in zip(error_codes, error_exceptions):
            with self.subTest(f"Status code: {code}"):
                # Mock the AsyncClient's post method to return an error code
                self.naiclient.client.post = AsyncMock(
                    return_value=MagicMock(status_code=code)
                )

                # Check if correct exception is raised
                with self.assertRaises(exception):
                    await self.naiclient.get_access_token()


if __name__ == "__main__":
    unittest.main()
