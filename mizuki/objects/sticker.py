from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from mizuki._utils import scls, sint
from mizuki.enums.sticker import StickerFormatType, StickerType
from mizuki.objects.asset import Asset
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.user import User
from mizuki.payloads.sticker import PartialStickerPayload, StickerPayload

if TYPE_CHECKING:
    from mizuki.state import ConnectionState

__all__ = (
    "PartialSticker",
    "Sticker",
)


class PartialSticker:
    __slots__ = ("id", "name", "format_type")

    def __init__(self, data: PartialStickerPayload, *, state: ConnectionState):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.format_type = StickerFormatType(data["format_type"])


class Sticker(PartialSticker):
    __slots__ = (
        "pack_id",
        "description",
        "tags",
        "type",
        "available",
        "guild_id",
        "user",
        "sort_value",
        "asset",
    )

    def __init__(self, data: StickerPayload, *, state: ConnectionState):
        super().__init__(data, state=state)
        self.pack_id = Snowflake._from_str(data.get("pack_id"))
        self.description = data["description"]
        self.tags = data["tags"]
        self.type = StickerType(data["type"])
        self.available = data.get("available", False)
        self.guild_id = sint(data.get("guild_id"))
        self.user = scls(User, data.get("user"), state=state)
        self.sort_value = data.get("sort_value")
        self.asset = Asset._from_sticker(self.format_type, self.id)

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented

    def __hash__(self) -> int:
        return self.id

    @property
    def created_at(self) -> datetime:
        return self.id.created_at
