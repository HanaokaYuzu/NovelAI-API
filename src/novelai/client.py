import asyncio
from asyncio import Task
from typing import Optional

from httpx import AsyncClient
from loguru import logger

from .consts import API_HOST, WEB_HOST, LOGIN_ENDPOINT, GENIMG_ENDPOINT, HEADERS
from .types import User, AuthError, APIError, NovelAIError
from .utils import get_access_key, parse_zip, running


class NAIClient:
    """
    Async httpx client interface to interact with NovelAI's service.
    """

    __slots__ = ["user", "running", "access_token", "close_task", "client"]

    def __init__(
        self,
        username: str,
        password: str,
        proxy: Optional[dict] = None,
    ):
        self.user = User(username=username, password=password)
        self.running: bool = False
        self.access_token: Optional[str] = None
        self.close_task: Optional[Task] = None
        self.client: AsyncClient = AsyncClient(
            timeout=30,
            proxies=proxy,
            headers=HEADERS,
        )

    async def get_access_token(self) -> str:
        """
        Login to NovelAI to get the access token.

        Parameters
        ----------
        username : `str`
            NovelAI username, usually an email address
        password : `str`
            NovelAI password

        Returns
        -------
        `str`
            NovelAI access token which is used in the Authorization header with the Bearer scheme
        """
        access_key = get_access_key(self.user)

        response = await self.client.post(
            url=f"{API_HOST}{LOGIN_ENDPOINT}",
            json={
                "key": access_key,
            },
        )

        match response.status_code:
            case 201:
                return response.json()["accessToken"]
            case 400:
                raise APIError("A validation error occured.")
            case 401:
                raise AuthError("Invalid username or password.")
            case _:
                raise NovelAIError("An unknown error occured.")

    async def init(self) -> None:
        """
        Get access token and implement Authorization header.
        """
        try:
            self.access_token = await self.get_access_token()
            self.client.headers["Authorization"] = f"Bearer {self.access_token}"
            self.running = True
            logger.success("NovelAI client initialized successfully.")
        except Exception as e:
            await self.client.aclose()
            logger.error(f"Failed to initiate client. {type(e).__name__}: {e}")

    async def close(self, timeout=300) -> None:
        """
        Close the client after a certain period of inactivity, or call manually to close immediately.
        """
        await asyncio.sleep(timeout)
        await self.client.aclose()

    async def reset_close_task(self) -> None:
        """
        Reset the timer for closing the client when a new request is made.
        """
        if self.close_task:
            self.close_task.cancel()
            self.close_task = None
        self.close_task = asyncio.create_task(self.close())

    @running
    async def generate_image(self, prompt: str, host="api") -> dict:
        """
        Generate an image from a prompt.

        Parameters
        ----------
        prompt : `str`
            Prompt to generate an image from
        host : `str`
            Host to send the request. Either "api" or "web"

        Returns
        -------
        `dict`
            Dictionary with file names (`str`) as keys and file contents (`bytes`) as values
        """
        assert prompt, "Prompt cannot be empty."

        assert host in (
            "api",
            "web",
        ), "Value of param `host` must be either 'api' or 'web'."
        HOST = host == "api" and API_HOST or WEB_HOST
        ACCEPT = host == "api" and "application/x-zip-compressed" or "binary/octet-stream"

        await self.reset_close_task()

        response = await self.client.post(
            url=f"{HOST}{GENIMG_ENDPOINT}",
            json={
                "input": prompt,
                "model": "nai-diffusion-3",
                "action": "generate",
                "parameters": {
                    "params_version": 1,
                    "width": 832,
                    "height": 1216,
                    "scale": 5.5,
                    "sampler": "k_euler",
                    "steps": 28,
                    "n_samples": 1,
                    "ucPreset": 0,
                    "qualityToggle": False,
                    "sm": True,
                    "sm_dyn": False,
                    "dynamic_thresholding": False,
                    "controlnet_strength": 1,
                    "legacy": False,
                    "add_original_image": True,
                    "uncond_scale": 1,
                    "cfg_rescale": 0,
                    "noise_schedule": "native",
                    "legacy_v3_extend": False,
                    "negative_prompt": "lowres, {bad}, text, error, missing, extra, fewer, cropped, jpeg artifacts, {{worst quality}}, bad quality, {{{watermark}}}, {{very displeasing}}, displeasing, unfinished, chromatic aberration, scan, scan artifacts, signature, extra digits, artistic error, username, [abstract],",
                },
            },
        )

        match response.status_code:
            case 200:
                assert (
                    response.headers["Content-Type"] == ACCEPT
                ), f"Invalid response content type. Expected '{ACCEPT}', got '{response.headers['Content-Type']}'."
                return parse_zip(response.content)
            case 400:
                raise APIError("A validation error occured.")
            case 401:
                raise AuthError("Access token is incorrect.")
            case 402:
                raise AuthError(
                    "An active subscription is required to access this endpoint."
                )
            case 409:
                raise APIError("A conflict error occured.")
            case _:
                raise NovelAIError("An unknown error occured.")
