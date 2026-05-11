from typing import Any
from .user import User
from .asset import Asset
from .snowflake import Snowflake
from datetime import datetime

class PartialEmoji:
    def __init__(self, data: dict[str, Any]):
        self.id = Snowflake._from_str(data["id"])
        self.animated: bool = data.get("animated", False)
        self.name: str | None = data["name"]
        self.asset: Asset | None = Asset._from_custom_emoji(self.id, self.animated) if self.id else None
        
    @property
    def created_at(self) -> datetime | None:
        return self.id.created_at if self.id else None
    
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, (PartialEmoji, Emoji)):
            if self.id is not None:
                return self.id == obj.id
            return self.name == obj.name
        return NotImplemented
        
    def __hash__(self) -> int:
        return hash(self.id or self.name)
        
class Emoji:
    def __init__(self, data: dict[str, Any]):
        self.id = Snowflake(data["id"])
        self.name: str = data["name"]
        self.role_ids: list[int] | None = data.get("roles") # maybe later when cache and everything is working ill do full zrole Obkects
        self.user = User._from_dict(data.get("user"))
        self.require_colons: bool = data.get("require_colons", False)
        self.managed: bool = data.get("managed", False)
        self.animated: bool = data.get("animated", False)
        self.available: bool = data.get("available", False)
        self.asset = Asset._from_custom_emoji(data, self.animated)
        
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
        
    def __hash__(self) -> int:
        return self.id
