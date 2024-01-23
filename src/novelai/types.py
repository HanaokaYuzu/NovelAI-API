from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str

    def __str__(self):
        return f"User(username={self.username})"


class AuthError(Exception):
    pass


class APIError(Exception):
    pass


class NovelAIError(Exception):
    pass
