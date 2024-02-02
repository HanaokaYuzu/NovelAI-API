import io
import zipfile
from hashlib import blake2b
from base64 import urlsafe_b64encode

import argon2

from .types import User


# https://github.com/Aedial/novelai-api/blob/main/novelai_api/utils.py
def encode_access_key(user: User) -> str:
    """
    Generate hashed access key from the user's username and password using the blake2 and argon2 algorithms.

    Parameters
    ----------
    user : `User`
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


def parse_zip(zip_data: bytes) -> dict:
    """
    Parse binary data of a zip file into a dictionary.

    Parameters
    ----------
    zip_data : `bytes`
        Binary data of a zip file

    Returns
    -------
    `dict`
        Dictionary containing pairs of filename (in `str`) and file data (in `bytes`) for each file in the zip
    """
    files = {}

    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
        for filename in zip_file.namelist():
            files[filename] = zip_file.read(filename)

    return files
