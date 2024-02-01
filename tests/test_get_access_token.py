import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from novelai import (
    NAIClient,
    User,
    APIError,
    AuthError,
    NovelAIError,
    HOSTS,
    ENDPOINTS,
)
from novelai.utils import encode_access_key


class TestNAIClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.username = "test_username"
        self.password = "test_password"
        self.user = User(username=self.username, password=self.password)
        self.naiclient = NAIClient(self.username, self.password)

    async def test_get_access_token(self):
        # Mock the AsyncClient's post method
        self.naiclient.client.post = AsyncMock(
            return_value=MagicMock(
                status_code=201,
                json=MagicMock(return_value={"accessToken": "test_token"}),
            )
        )

        # Run the method and check the result
        result = await self.naiclient.get_access_token()
        self.assertEqual(result, "test_token")

        # Check that the post method was called with the correct arguments
        self.naiclient.client.post.assert_awaited_once_with(
            url=f"{HOSTS.API.url}{ENDPOINTS.LOGIN}",
            json={
                "key": encode_access_key(self.user),
            },
        )

    def test_get_access_token_error(self):
        # Test the error cases
        error_codes = [400, 401, 500]
        error_exceptions = [APIError, AuthError, NovelAIError]

        for code, exception in zip(error_codes, error_exceptions):
            with self.subTest(code=code):
                # Mock the AsyncClient's post method to return an error code
                self.naiclient.client.post = AsyncMock(
                    return_value=MagicMock(status_code=code)
                )

                # Check that the correct exception is raised
                with self.assertRaises(exception):
                    asyncio.run(self.naiclient.get_access_token())


if __name__ == "__main__":
    unittest.main()
