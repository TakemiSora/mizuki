from enum import StrEnum

__all__ = (
    "EmbedType",
)

class EmbedType(StrEnum):
    rich = "rich"
    image = "image"
    video = "video"
    gifv = "gifv"
    article = "article"
    link = "link"
    poll_result = "poll_result"