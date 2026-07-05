from enum import IntEnum

__all__ = ("StickerType", "StickerFormatType")


class StickerType(IntEnum):
    STICKER = 1
    GUILD = 2


class StickerFormatType(IntEnum):
    PNG = 1
    APNG = 2
    LOTTIE = 3
    GIF = 4

    def __str__(self) -> str:
        return {1: "png", 2: "png", 3: "lottie", 4: "gif"}[self.value]
