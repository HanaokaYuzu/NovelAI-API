from pydantic import BaseModel


class User(BaseModel):
    """
    NovelAI credentials for user account authentication.
    """

    username: str
    password: str

    def __str__(self):
        return f"User(username={self.username})"

    __repr__ = __str__
