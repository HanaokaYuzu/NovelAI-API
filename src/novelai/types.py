from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str

    def __str__(self):
        return f"User(username={self.username})"


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
