from typing import Optional

from httpx import AsyncClient

from .consts import HEADERS


class NAIClient:
    __slots__ = ["running", "access_token", "client"]

    def __init__(
        self,
        access_token: str,
        proxy: Optional[dict] = None,
    ):
        self.running: bool = False
        self.access_token: Optional[str] = access_token
        self.client: AsyncClient = AsyncClient(
            timeout=20,
            proxies=proxy,
            follow_redirects=True,
            headers=HEADERS,
        )
