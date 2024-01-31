from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class DotDict(dict):
    """
    Dictionary with dot notation access to its keys.
    """
    def __getattr__(self, name):
        return self.get(name, None)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


class User(BaseModel):
    """
    NovelAI credentials for user account authentication.
    """
    username: str
    password: str

    def __str__(self):
        return f"User(username={self.username})"

    __repr__ = __str__


@dataclass(frozen=True, kw_only=True, slots=True)
class Host:
    """
    Hostnames of NovelAI services and corresponding accepted content types.
    """

    url: str
    accept: str


class AuthError(Exception):
    """
    Exception for account authentication errors.
    """

    pass


class APIError(Exception):
    """
    Exception for package-level errors which need to be fixed in the future development (e.g. validation errors).
    """

    pass


class NovelAIError(Exception):
    """
    Exception for errors returned from NovelAI which are not handled by the package.
    """

    pass
