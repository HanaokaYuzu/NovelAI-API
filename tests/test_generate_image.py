import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from novelai import (
    NAIClient,
    User,
    APIError,
    AuthError,
    NovelAIError,
    Metadata,
    MODELS,
    ACTIONS,
    HOSTS,
    ENDPOINTS,
)
from novelai.utils import parse_zip


class TestNAIClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.username = "test_username"
        self.password = "test_password"
        self.zipdata = b"PK\x05\x06" + b"\x00" * 18
        self.user = User(username=self.username, password=self.password)
        self.naiclient = NAIClient(self.username, self.password)
        self.naiclient.running = True

    async def test_generate_image(self):
        # Mock the AsyncClient's post method
        self.naiclient.client.post = AsyncMock(
            return_value=MagicMock(
                status_code=200,
                headers={"Content-Type": HOSTS.API.accept},
                content=self.zipdata,
            )
        )

        # Run the method and check the result
        result = await self.naiclient.generate_image(
            Metadata(
                prompt="test_prompt",
                model=MODELS.V3,
                action=ACTIONS.GENERATE,
                qualityToggle=False,
            )
        )
        self.assertEqual(result, parse_zip(self.zipdata))

        # Check that the post method was called with the correct arguments
        self.naiclient.client.post.assert_awaited_once_with(
            url=f"{HOSTS.API.url}{ENDPOINTS.IMAGE}",
            json={
                "input": "test_prompt",
                "model": MODELS.V3,
                "action": ACTIONS.GENERATE,
                "parameters": Metadata(
                    prompt="test_prompt", qualityToggle=False
                ).model_dump(exclude_none=True),
            },
        )

    def test_generate_image_error(self):
        # Test the error cases
        error_codes = [400, 401, 402, 409, 500]
        error_exceptions = [APIError, AuthError, AuthError, APIError, NovelAIError]

        for code, exception in zip(error_codes, error_exceptions):
            with self.subTest(code=code):
                # Mock the AsyncClient's post method to return an error code
                self.naiclient.client.post = AsyncMock(
                    return_value=MagicMock(status_code=code)
                )

                # Check that the correct exception is raised
                with self.assertRaises(exception):
                    asyncio.run(
                        self.naiclient.generate_image(
                            Metadata(
                                prompt="test_prompt",
                                model=MODELS.V3,
                                action=ACTIONS.GENERATE,
                            )
                        )
                    )


if __name__ == "__main__":
    unittest.main()
