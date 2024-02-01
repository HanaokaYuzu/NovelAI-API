import asyncio
from asyncio import Task
from typing import Optional

from httpx import AsyncClient, ReadTimeout
from pydantic import validate_call
from loguru import logger

from .consts import HOSTS, ENDPOINTS, HEADERS
from .types import Host, User, AuthError, APIError, NovelAIError
from .utils import encode_access_key, parse_zip, running
from .metadata import Metadata


class NAIClient:
    """
    Async httpx client interface to interact with NovelAI's service.

    Parameters
    ----------
    username: `str`
        NovelAI username, usually an email address
    password: `str`
        NovelAI password
    timeout: `int`, optional
        Timeout for the client in seconds. Used for limiting the max waiting time of a request
    proxy: `dict`, optional
        Proxy to use for the client
    """

    __slots__ = ["user", "running", "access_token", "close_task", "client"]

    def __init__(
        self,
        username: str,
        password: str,
        timeout: int = 30,
        proxy: Optional[dict] = None,
    ):
        self.user = User(username=username, password=password)
        self.running: bool = False
        self.access_token: Optional[str] = None
        self.close_task: Optional[Task] = None
        self.client: AsyncClient = AsyncClient(
            timeout=timeout,
            proxies=proxy,
            headers=HEADERS,
        )

    async def get_access_token(self) -> str:
        """
        Send post request to /user/login endpoint to get user's access token.

        Returns
        -------
        `str`
            NovelAI access token which is used in the Authorization header with the Bearer scheme
        """
        access_key = encode_access_key(self.user)

        response = await self.client.post(
            url=f"{HOSTS.API.url}{ENDPOINTS.LOGIN}",
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
    @validate_call
    async def generate_image(
        self,
        metadata: Metadata | None = None,
        host: Host = HOSTS.API,
        verbose: bool = False,
        is_opus: bool = False,
        **kwargs,
    ) -> dict:
        """
        Send post request to /ai/generate-image endpoint for image generation.

        Parameters
        ----------
        metadata: `Metadata`
            Metadata object containing parameters required for image generation
        host: `Host`, optional
            Host to send the request. Refer to `novelai.consts.HOSTS` for available hosts or provide a custom host
        verbose: `bool`, optional
            If `True`, will log the estimated Anlas cost before sending the request
        is_opus: `bool`, optional
            Use with `verbose` to calculate the cost based on your subscription tier
        **kwargs: `Any`
            If `metadata` is not provided, these parameters are used to create a `Metadata` object

        Returns
        -------
        `dict`
            Dictionary with file names (`str`) as keys and file contents (`bytes`) as values
        """
        if metadata is None:
            metadata = Metadata(**kwargs)

        if verbose:
            logger.info(f"Estimated Anlas cost: {metadata.calculate_cost(is_opus)}")

        await self.reset_close_task()

        try:
            response = await self.client.post(
                url=f"{host.url}{ENDPOINTS.IMAGE}",
                json={
                    "input": metadata.prompt,
                    "model": metadata.model,
                    "action": metadata.action,
                    "parameters": metadata.model_dump(exclude_none=True),
                },
            )
        except ReadTimeout:
            raise NovelAIError(
                "Request timed out. Please try again. If the problem persists, consider setting a higher `timeout` value when initiating NAIClient."
            )

        match response.status_code:
            case 200:
                assert (
                    response.headers["Content-Type"] == host.accept
                ), f"Invalid response content type. Expected '{host.accept}', got '{response.headers['Content-Type']}'."
                return parse_zip(response.content)
            case 400:
                raise APIError(
                    f"A validation error occured. Message from NovelAI: {response.json().get('message')}"
                )
            case 401:
                raise AuthError(
                    f"Access token is incorrect. Message from NovelAI: {response.json().get('message')}"
                )
            case 402:
                raise AuthError(
                    f"An active subscription is required to access this endpoint. Message from NovelAI: {response.json().get('message')}"
                )
            case 409:
                raise APIError(
                    f"A conflict error occured. Message from NovelAI: {response.json().get('message')}"
                )
            case _:
                raise NovelAIError(
                    f"An unknown error occured. Error message: {response.status_code} {response.reason_phrase}"
                )
