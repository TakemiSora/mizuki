from __future__ import annotations
from typing import Any, Literal
from .asset import Asset

# currently a flat nameplate type instead of collectibles until discord has another collectible type
class Nameplate:
    ValidPaletteType = Literal["crimson", "berry", "sky", "teal", "forest", "bubble_gum", "violet", "cobalt", "clover", "lemon", "white"]

    def __init__(self, data: dict[str, Any]):            
        self.sku_id = int(data["sku_id"])
        self.asset = Asset._from_collectibles_nameplate(data["asset"])
        self.label = data["label"]
        self.palette: Nameplate.ValidPaletteType = data["palette"]

    @classmethod
    def _from_dict(cls, data: dict[str, Any] | None) -> Nameplate | None:
        if data is not None:
            return cls(data)
        return None
    
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.sku_id == obj.sku_id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.sku_id
