from __future__ import annotations
from .asset import Asset
from .snowflake import Snowflake
from datetime import datetime
from ..payloads.avatar_decoration import AvatarDecorationPayload

__all__ = (
    "AvatarDecoration",
)

class AvatarDecoration:
    __slots__ = (
        "sku_id",
        "asset"
    )
    
    def __init__(self, data: AvatarDecorationPayload):
        self.sku_id = Snowflake(data["sku_id"])
        self.asset = Asset._from_user_avatar_decoration(data["asset"])

    @property
    def created_at(self) -> datetime:
        return self.sku_id.created_at

    @classmethod
    def _from_dict(cls, data: AvatarDecorationPayload | None) -> AvatarDecoration | None:
        if data is not None:
            return cls(data)
        return None

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.sku_id == obj.sku_id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.sku_id