import io
import zipfile
from typing import Generator
from base64 import urlsafe_b64encode
from hashlib import blake2b

import argon2

from .types import User
from .exceptions import APIError, AuthError, NovelAIError, ConcurrentError


# https://github.com/Aedial/novelai-api/blob/main/novelai_api/utils.py
def encode_access_key(user: User) -> str:
    """
    Generate hashed access key from the user's username and password using the blake2 and argon2 algorithms.

    Parameters
    ----------
    user : `novelai.types.User`
        User object containing username and password

    Returns
    -------
    `str`
        Hashed access key
    """
    pre_salt = f"{user.password[:6]}{user.username}novelai_data_access_key"

    blake = blake2b(digest_size=16)
    blake.update(pre_salt.encode())
    salt = blake.digest()

    raw = argon2.low_level.hash_secret_raw(
        secret=user.password.encode(),
        salt=salt,
        time_cost=2,
        memory_cost=int(2000000 / 1024),
        parallelism=1,
        hash_len=64,
        type=argon2.low_level.Type.ID,
    )
    hashed = urlsafe_b64encode(raw).decode()

    return hashed[:64]


class ResponseParser:
    """
    A helper class to parse the response from NovelAI's API.

    Parameters
    ----------
    response : `httpx.Response`
        Response object from the API
    """

    def __init__(self, response):
        self.response = response

    def handle_status_code(self):
        """
        Handle the status code of the response.

        Raises
        ------
        `novelai.exceptions.APIError`
            If the status code is 400
        `novelai.exceptions.AuthError`
            If the status code is 401 or 402
        `novelai.exceptions.ConcurrentError`
            If the status code is 429
        `novelai.exceptions.NovelAIError`
            If the status code is 409 or any other unknown status code
        """
        match self.response.status_code:
            case 200 | 201:
                return
            case 400:
                raise APIError(
                    f"A validation error occured. Message from NovelAI: {self.response.json().get('message')}"
                )
            case 401:
                self.running = False
                raise AuthError(
                    f"Access token is incorrect. Message from NovelAI: {self.response.json().get('message')}"
                )
            case 402:
                self.running = False
                raise AuthError(
                    f"An active subscription is required to access this endpoint. Message from NovelAI: {self.response.json().get('message')}"
                )
            case 409:
                raise NovelAIError(
                    f"A conflict error occured. Message from NovelAI: {self.response.json().get('message')}"
                )
            case 429:
                raise ConcurrentError(
                    f"A concurrent error occured. Message from NovelAI: {self.response.json().get('message')}"
                )
            case _:
                raise NovelAIError(
                    f"An unknown error occured. Error message: {self.response.status_code} {self.response.reason_phrase}"
                )

    def parse_zip_content(self) -> Generator[bytes, None, None]:
        """
        Parse binary data of a zip file into a dictionary.

        Parameters
        ----------
        zip_data : `bytes`
            Binary data of a zip file

        Returns
        -------
        `Generator`
            A generator of binary data of all files in the zip
        """
        with zipfile.ZipFile(io.BytesIO(self.response.content)) as zip_file:
            for filename in zip_file.namelist():
                yield zip_file.read(filename)
