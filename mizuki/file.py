import pathlib
from ._utils import _MISSING

__all__ = (
    "File",
)

class File:
    __slots__ = (
        "path",
        "description",
        "filename",
        "spoiler",
        "url"
    )

    def __init__(
        self, path: str,
        *, filename: str = _MISSING,
        spoiler: bool = _MISSING,
        description: bool = _MISSING
    ):
        self.path = pathlib.Path(path)
        self.spoiler = spoiler
        self.description = description
        self.filename = ("SPOILER_" if spoiler else "") + (filename if filename else self.path.name)
        self.url = f"attachment://{self.filename}"