from typing import TypedDict, NotRequired


class FileUploadPayload(TypedDict):
    id: int
    filename: str
    description: NotRequired[str]
