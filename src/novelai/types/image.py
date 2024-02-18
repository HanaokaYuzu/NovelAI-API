from pathlib import Path

from pydantic import BaseModel
from loguru import logger

from .metadata import Metadata


class Image(BaseModel):
    """
    A single image object in the return of `generate_image` method.
    """

    filename: str
    data: bytes
    metadata: Metadata

    def __str__(self):
        return f"Image(filename={self.filename})"

    __repr__ = __str__

    def save(
        self, path: str = "temp", filename: str | None = None, verbose: bool = False
    ):
        """
        Save image to local file.

        Parameters
        ----------
        path : `str`, optional
            Path to save the image, by default will save to ./temp
        filename : `str`, optional
            Filename of the saved file, by default will use `self.filename`
            If provided, `self.filename` will also be updated to match this value
        verbose : `bool`, optional
            If True, print the path of the saved file, by default False
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        self.filename = filename or self.filename
        dest = path / self.filename
        dest.write_bytes(self.data)

        if verbose:
            logger.info(f"Image saved as {dest.resolve()}")
