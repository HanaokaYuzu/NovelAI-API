import os
import base64
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

from novelai import NAIClient, Metadata, Host, Model, Action, Resolution
from novelai.exceptions import (
    APIError,
    AuthError,
    ConcurrentError,
    TimeoutError,
    NovelAIError,
)


with open("tests/images/portrait.jpg", "rb") as f:
    base_image = base64.b64encode(f.read()).decode("utf-8")

with open("tests/images/inpaint_left.jpg", "rb") as f:
    mask = base64.b64encode(f.read()).decode("utf-8")


class TestGenerateImage(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.naiclient = NAIClient(
            os.getenv("USERNAME") or "test_username",
            os.getenv("PASSWORD") or "test_password",
        )

    @unittest.skipIf(
        not (os.getenv("USERNAME") and os.getenv("PASSWORD")),
        "Skipped due to missing environment variables",
    )
    async def test_generate(self):
        await self.naiclient.init()
        metadata = Metadata(prompt="1girl")

        async def task_api():
            with self.subTest("task_api"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=Host.API
                    )
                    self.assertTrue(len(output) > 0)
                    for image in output:
                        image.save(filename="generate_api.png", verbose=True)
                        self.assertTrue(image.filename == "generate_api.png")
                except ConcurrentError:
                    self.skipTest("task_api raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_api timed out")

        async def task_web():
            with self.subTest("task_web"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=Host.WEB
                    )
                    self.assertTrue(len(output) > 0)
                    for image in output:
                        image.save(filename="generate_web.png", verbose=True)
                        self.assertTrue(image.filename == "generate_web.png")
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
        await self.naiclient.init()
        metadata = Metadata(
            prompt="1girl",
            action=Action.IMG2IMG,
            res_preset=Resolution.NORMAL_PORTRAIT,
            image=base_image,
            strength=0.45,
            noise=0.1,
        )

        async def task_api():
            with self.subTest("task_api"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=Host.API
                    )
                    self.assertTrue(len(output) > 0)
                    for image in output:
                        image.save(filename="img2img_api.png", verbose=True)
                except ConcurrentError:
                    self.skipTest("task_api raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_api timed out")

        async def task_web():
            with self.subTest("task_web"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=Host.WEB
                    )
                    self.assertTrue(len(output) > 0)
                    for image in output:
                        image.save(filename="img2img_web.png", verbose=True)
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
        await self.naiclient.init()
        metadata = Metadata(
            prompt="1girl",
            model=Model.V3INP,
            action=Action.INPAINT,
            res_preset=Resolution.NORMAL_PORTRAIT,
            image=base_image,
            mask=mask,
        )

        async def task_api():
            with self.subTest("task_api"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=Host.API
                    )
                    self.assertTrue(len(output) > 0)
                    for image in output:
                        image.save(filename="inpaint_api.png", verbose=True)
                except ConcurrentError:
                    self.skipTest("task_api raised concurrent error")
                except TimeoutError:
                    self.skipTest("task_api timed out")

        async def task_web():
            with self.subTest("task_web"):
                try:
                    output = await self.naiclient.generate_image(
                        metadata, host=Host.WEB
                    )
                    self.assertTrue(len(output) > 0)
                    for image in output:
                        image.save(filename="inpaint_web.png", verbose=True)
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
        self.naiclient.client = AsyncClient()
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
