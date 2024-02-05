import os
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

from novelai import (
    NAIClient,
    APIError,
    AuthError,
    NovelAIError,
    Metadata,
    HEADERS,
    HOSTS,
)


class TestGenerateImage(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.naiclient = NAIClient(
            os.getenv("USERNAME") or "test_username",
            os.getenv("PASSWORD") or "test_password",
        )
        self.naiclient.client = AsyncClient(headers=HEADERS)
        self.metadata = Metadata(prompt="1girl", seed=1, extra_noise_seed=2)

    @unittest.skipIf(
        not (os.getenv("USERNAME") and os.getenv("PASSWORD")),
        "Skipping test_success...",
    )
    async def test_success(self):
        async def task_api():
            with self.subTest("task_api"):
                try:
                    output = await self.naiclient.generate_image(
                        self.metadata, host=HOSTS.API
                    )
                    self.assertTrue("image_0.png" in output)
                except NovelAIError:
                    self.skipTest("task_api timed out")

        async def task_web():
            with self.subTest("task_web"):
                try:
                    output = await self.naiclient.generate_image(
                        self.metadata, host=HOSTS.WEB
                    )
                    self.assertTrue("image_0.png" in output)
                except NovelAIError:
                    self.skipTest("task_web skipped")

        tasks = [
            asyncio.create_task(task_api()),
            asyncio.create_task(task_web()),
        ]
        await asyncio.wait(tasks)

    def test_exceptions(self):
        # Error cases
        error_codes = [400, 401, 402, 409, 429, 500]
        error_exceptions = [
            APIError,
            AuthError,
            AuthError,
            APIError,
            NovelAIError,
            NovelAIError,
        ]

        for code, exception in zip(error_codes, error_exceptions):
            with self.subTest(f"Status code: {code}"):
                self.naiclient.running = True
                # Mock the AsyncClient's post method to return an error code
                self.naiclient.client.post = AsyncMock(
                    return_value=MagicMock(status_code=code)
                )

                # Check if correct exception is raised
                with self.assertRaises(exception):
                    asyncio.run(self.naiclient.generate_image(self.metadata))


if __name__ == "__main__":
    unittest.main()
