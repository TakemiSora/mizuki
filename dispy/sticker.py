from typing import Any
from .utils import sint
from .enums import StickerType, StickerFormatType
from .asset import Asset
from .user import User
from .snowflake import Snowflake
from datetime import datetime

class Sticker:
    def __init__(self, data: dict[str, Any]):
        self.id = Snowflake(data["id"])
        self.pack_id = Snowflake._from_str(data.get("pack_id"))
        self.name: str = data["name"]
        self.description: str | None = data["description"]
        self.tags: str = data["tags"]
        self.type = StickerType(data["type"])
        self.format_type = StickerFormatType(data["format_type"])
        self.available: bool = data.get("available", False)
        self.guild_id = sint(data.get("guild_id"))
        self.user = User._from_dict(data.get("user"))
        self.sort_value = sint(data.get("sort_value"))
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