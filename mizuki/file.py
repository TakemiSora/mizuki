import pathlib
from typing import Any
from ._utils import _MISSING, assign_val_dict

__all__ = (
    "File",
)

class File:
    """
    Represents a Discord File to be sent to Discord.

    Parameters
    ----------
    path : :class:`str`
        The relative or absolute path of the file to send.

    description : :class:`str`, optional
        The description of the file. Appears as alternative text, only supported for media files.

    filename : :class:`str`, optional
        The name to upload the file as. Defaults to the name of the file given via path parameter.

    spoiler : :class:`bool`, optional
        Whether to spoiler the media to send. Only works for media files.
    """

    __slots__ = (
        "path",
        "description",
        "filename",
        "spoiler",
        "url"
    )

    path: pathlib.Path
    "The :class:`pathlib.Path` object for the file provided."

    spoiler: bool
    "Whether the file is to be spoilered."

    description: str | None
    "The description of the file."

    filename: str
    "The filename that will be used when uploading."

    url: str
    "The attachment:// format URL for this file object."

    def __init__(
        self, path: str,
        *, filename: str = _MISSING,
        spoiler: bool = False,
        description: str | None = None
    ):
        self.path = pathlib.Path(path)
        self.spoiler = spoiler
        self.description = description
        self.filename = ("SPOILER_" if spoiler else "") + (filename if filename else self.path.name)
        self.url = f"attachment://{self.filename}"

    def _to_attachment_dict(self, id: int) -> dict[str, Any]:
        return assign_val_dict(
            {},
            id=id,
            filename=self.filename,
            description=self.description
        )