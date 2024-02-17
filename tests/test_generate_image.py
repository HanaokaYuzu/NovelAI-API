import os
import base64
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from httpx import AsyncClient

from novelai import (
    NAIClient,
    APIError,
    AuthError,
    NovelAIError,
    ConcurrentError,
    TimeoutError,
    Metadata,
    HEADERS,
    HOSTS,
    MODELS,
    ACTIONS,
    RESOLUTIONS,
)


with open("tests/images/portrait.jpg", "rb") as f:
    base_image = base64.b64encode(f.read()).decode("utf-8")

with open("tests/images/inpaint_left.jpg", "rb") as f:
    mask = base64.b64encode(f.read()).decode("utf-8")

output_path = Path("temp")
output_path.mkdir(parents=True, exist_ok=True)


class TestGenerateImage(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.naiclient = NAIClient(
            os.getenv("USERNAME") or "test_username",
            os.getenv("PASSWORD") or "test_password",
        )
        self.naiclient.client = AsyncClient(headers=HEADERS)

    @unittest.skipIf(
        not (os.getenv("USERNAME") and os.getenv("PASSWORD")),
        "Skipped due to missing environment variables",
    )
    async def test_generate(self):
        metadata = Metadata(prompt="1girl", seed=1, extra_noise_seed=2)

        async def task_api():
            with self.subTest("task_api"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=HOSTS.API
                    )
                    self.assertTrue("image_0.png" in output)
                    Path(output_path / "generate_api.png").write_bytes(
                        output["image_0.png"]
                    )
                except ConcurrentError:
                    self.skipTest("task_api raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_api timed out")

        async def task_web():
            with self.subTest("task_web"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=HOSTS.WEB
                    )
                    self.assertTrue("image_0.png" in output)
                    Path(output_path / "generate_web.png").write_bytes(
                        output["image_0.png"]
                    )
                except ConcurrentError:
                    self.skipTest("task_web raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_web timed out")

        tasks = [
            asyncio.create_task(task_api()),
            asyncio.create_task(task_web()),
        ]
        await asyncio.wait(tasks)

    @unittest.skipIf(
        not (os.getenv("USERNAME") and os.getenv("PASSWORD")),
        "Skipped due to missing environment variables",
    )
    async def test_img2img(self):
        metadata = Metadata(
            prompt="1girl",
            action=ACTIONS.IMG2IMG,
            width=RESOLUTIONS.NORMAL_PORTRAIT[0],
            height=RESOLUTIONS.NORMAL_PORTRAIT[1],
            image=base_image,
            strength=0.45,
            noise=0.1,
        )

        async def task_api():
            with self.subTest("task_api"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=HOSTS.API
                    )
                    self.assertTrue("image_0.png" in output)
                    Path(output_path / "img2img_api.png").write_bytes(
                        output["image_0.png"]
                    )
                except ConcurrentError:
                    self.skipTest("task_api raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_api timed out")

        async def task_web():
            with self.subTest("task_web"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=HOSTS.WEB
                    )
                    self.assertTrue("image_0.png" in output)
                    Path(output_path / "img2img_web.png").write_bytes(
                        output["image_0.png"]
                    )
                except ConcurrentError:
                    self.skipTest("task_web raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_web timed out")

        tasks = [
            asyncio.create_task(task_api()),
            asyncio.create_task(task_web()),
        ]
        await asyncio.wait(tasks)

    @unittest.skipIf(
        not (os.getenv("USERNAME") and os.getenv("PASSWORD")),
        "Skipped due to missing environment variables",
    )
    async def test_inpaint(self):
        metadata = Metadata(
            prompt="1girl",
            model=MODELS.V3INP,
            action=ACTIONS.INPAINT,
            width=RESOLUTIONS.NORMAL_PORTRAIT[0],
            height=RESOLUTIONS.NORMAL_PORTRAIT[1],
            image=base_image,
            mask=mask,
        )

        async def task_api():
            with self.subTest("task_api"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=HOSTS.API
                    )
                    self.assertTrue("image_0.png" in output)
                    Path(output_path / "inpaint_api.png").write_bytes(
                        output["image_0.png"]
                    )
                except ConcurrentError:
                    self.skipTest("task_api raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_api timed out")

        async def task_web():
            with self.subTest("task_web"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=HOSTS.WEB
                    )
                    self.assertTrue("image_0.png" in output)
                    Path(output_path / "inpaint_web.png").write_bytes(
                        output["image_0.png"]
                    )
                except ConcurrentError:
                    self.skipTest("task_web raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_web timed out")

        tasks = [
            asyncio.create_task(task_api()),
            asyncio.create_task(task_web()),
        ]
        await asyncio.wait(tasks)

    def test_exceptions(self):
        metadata = Metadata(prompt="1girl", seed=1, extra_noise_seed=2)
        error_codes = [400, 401, 402, 409, 429, 500]
        error_exceptions = [
            APIError,
            AuthError,
            AuthError,
            NovelAIError,
            ConcurrentError,
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
                    asyncio.run(self.naiclient.generate_image(metadata))


if __name__ == "__main__":
    unittest.main()
