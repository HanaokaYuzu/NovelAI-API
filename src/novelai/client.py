import asyncio
from asyncio import Task
from datetime import datetime

from httpx import AsyncClient, ReadTimeout
from pydantic import validate_call
from loguru import logger

from .types import User, Metadata, Image
from .constant import Host, Endpoint, HEADERS
from .exceptions import AuthError, TimeoutError
from .utils import ResponseParser, encode_access_key


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

        Raises
        ------
        `novelai.exceptions.AuthError`
            If the account credentials are incorrect
        """
        access_key = encode_access_key(self.user)

        response = await self.client.post(
            url=f"{Host.API.value.url}{Endpoint.LOGIN.value}",
            json={
                "key": access_key,
            },
        )

        # Exceptions are handled in self.init
        ResponseParser(response).handle_status_code()

        return response.json()["accessToken"]

    @running
    @validate_call
    async def generate_image(
        self,
        metadata: Metadata | None = None,
        host: Host = Host.WEB,
        verbose: bool = False,
        is_opus: bool = False,
        **kwargs,
    ) -> list[Image]:
        """
        Send post request to /ai/generate-image endpoint for image generation.

        Parameters
        ----------
        metadata: `novelai.Metadata`
            Metadata object containing parameters required for image generation
        host: `Host`, optional
            Host to send the request. Refer to `novelai.consts.Host` for available hosts or provide a custom host
        verbose: `bool`, optional
            If `True`, will log the estimated Anlas cost before sending the request
        is_opus: `bool`, optional
            Use with `verbose` to calculate the cost based on your subscription tier
        **kwargs: `Any`
            If `metadata` is not provided, these parameters are used to create a `novelai.Metadata` object

        Returns
        -------
        `list[novelai.Image]`
            List of `Image` objects containing the generated image and its metadata

        Raises
        ------
        `novelai.exceptions.TimeoutError`
            If the request time exceeds the client's timeout value
        `novelai.exceptions.AuthError`
            If the access token is incorrect or expired
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
                url=f"{host.value.url}{Endpoint.IMAGE.value}",
                json={
                    "input": metadata.prompt,
                    "model": metadata.model.value,
                    "action": metadata.action.value,
                    "parameters": metadata.model_dump(mode="json", exclude_none=True),
                },
            )
        except ReadTimeout:
            raise TimeoutError(
                "Request timed out, please try again. If the problem persists, consider setting a higher `timeout` value when initiating NAIClient."
            )

        try:
            ResponseParser(response).handle_status_code()
        except AuthError:
            await self.close(0)
            raise

        assert (
            response.headers["Content-Type"] == host.value.accept
        ), f"Invalid response content type. Expected '{host.value.accept}', got '{response.headers['Content-Type']}'."

        return [
            Image(filename=f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_{host.name.lower()}_p{i}.png", data=data, metadata=metadata)
            for i, data in enumerate(ResponseParser(response).parse_zip_content())
        ]
