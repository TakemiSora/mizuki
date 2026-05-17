from __future__ import annotations
from .asset import Asset
from .snowflake import Snowflake
from datetime import datetime
from ..payloads.collectibles import NameplatePayload

__all__ = (
    "Nameplate",
)

# currently a flat nameplate type instead of collectibles until discord has another collectible type
class Nameplate:
    __slots__ = (
        "sku_id",
        "asset",
        "label",
        "palette"
    )
    
    def __init__(self, data: NameplatePayload):            
        self.sku_id = Snowflake(data["sku_id"])
        self.asset = Asset._from_collectibles_nameplate(data["asset"])
        self.label = data["label"]
        self.palette= data["palette"]
        
    @property
    def created_at(self) -> datetime:
        return self.sku_id.created_at

    @classmethod
    def _from_dict(cls, data: NameplatePayload | None) -> Nameplate | None:
        if data is not None:
            return cls(data)
        return None
    
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.sku_id == obj.sku_id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.sku_id
