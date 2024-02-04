import asyncio
from asyncio import Task

from httpx import AsyncClient, ReadTimeout
from pydantic import validate_call
from loguru import logger

from .consts import HOSTS, ENDPOINTS, HEADERS
from .types import Host, User, AuthError, APIError, NovelAIError
from .utils import encode_access_key, parse_zip
from .metadata import Metadata


def running(func) -> callable:
    """
    Decorator to check if client is running before making a request.
    """

    async def wrapper(self: "NAIClient", *args, **kwargs):
        if not self.running:
            await self.init(auto_close=self.auto_close, close_delay=self.close_delay)
            if self.running:
                return await func(self, *args, **kwargs)

            raise Exception(
                f"Invalid function call: NAIClient.{func.__name__}. Client initialization failed."
            )
        else:
            return await func(self, *args, **kwargs)

    return wrapper


class NAIClient:
    """
    Async httpx client interface to interact with NovelAI's service.

    Parameters
    ----------
    username: `str`
        NovelAI username, usually an email address
    password: `str`
        NovelAI password
    proxy: `dict`, optional
        Proxy to use for the client
    """

    __slots__ = [
        "user",
        "proxy",
        "client",
        "running",
        "auto_close",
        "close_delay",
        "close_task",
    ]

    def __init__(
        self,
        username: str,
        password: str,
        proxy: dict | None = None,
    ):
        self.user = User(username=username, password=password)
        self.proxy = proxy
        self.client: AsyncClient | None = None
        self.running: bool = False
        self.auto_close: bool = False
        self.close_delay: int = 0
        self.close_task: Task | None = None

    async def init(
        self, timeout: float = 30, auto_close: bool = False, close_delay: int = 300
    ) -> None:
        """
        Get access token and implement Authorization header.

        Parameters
        ----------
        timeout: `int`, optional
            Request timeout of the client in seconds. Used to limit the max waiting time when sending a request
        auto_close: `bool`, optional
            If `True`, the client will close connections and clear resource usage after a certain period
            of inactivity. Useful for keep-alive services
        close_delay: `int`, optional
            Time to wait before auto-closing the client in seconds. Effective only if `auto_close` is `True`
        """
        try:
            self.client = AsyncClient(
                timeout=timeout, proxies=self.proxy, headers=HEADERS
            )
            self.client.headers["Authorization"] = (
                f"Bearer {await self.get_access_token()}"
            )

            self.running = True
            logger.success("NovelAI client initialized successfully.")

            self.auto_close = auto_close
            self.close_delay = close_delay
            if self.auto_close:
                await self.reset_close_task()
        except Exception:
            await self.close(0)
            raise

    async def close(self, wait: int | None = None) -> None:
        """
        Close the client after a certain period of inactivity, or call manually to close immediately.

        Parameters
        ----------
        wait: `int`, optional
            Time to wait before closing the client in seconds
        """
        await asyncio.sleep(wait is not None and wait or self.close_delay)
        await self.client.aclose()
        self.running = False

    async def reset_close_task(self) -> None:
        """
        Reset the timer for closing the client when a new request is made.
        """
        if self.close_task:
            self.close_task.cancel()
            self.close_task = None
        self.close_task = asyncio.create_task(self.close())

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
                raise NovelAIError(
                    f"An unknown error occured. Error message: {response.status_code} {response.reason_phrase}"
                )

    @running
    @validate_call
    async def generate_image(
        self,
        metadata: Metadata | None = None,
        host: Host = HOSTS.API,
        verbose: bool = False,
        is_opus: bool = False,
        **kwargs,
    ) -> dict[str, bytes]:
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
            logger.info(
                f"Generating image... estimated Anlas cost: {metadata.calculate_cost(is_opus)}"
            )

        if self.auto_close:
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
                "Request timed out, please try again. If the problem persists, consider setting a higher `timeout` value when initiating NAIClient."
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
                self.running = False
                raise AuthError(
                    f"Access token is incorrect. Message from NovelAI: {response.json().get('message')}"
                )
            case 402:
                self.running = False
                raise AuthError(
                    f"An active subscription is required to access this endpoint. Message from NovelAI: {response.json().get('message')}"
                )
            case 409:
                raise APIError(
                    f"A conflict error occured. Message from NovelAI: {response.json().get('message')}"
                )
            case 429:
                raise NovelAIError(
                    f"A concurrent error occured. Message from NovelAI: {response.json().get('message')}"
                )
            case _:
                raise NovelAIError(
                    f"An unknown error occured. Error message: {response.status_code} {response.reason_phrase}"
                )
