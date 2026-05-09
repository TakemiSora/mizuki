from __future__ import annotations
from typing import Any, Literal
from .state import State
from .asset import Asset

# currently a flat nameplate type instead of collectibles until discord has another collectible type
class Nameplate:
    ValidPaletteType = Literal["crimson", "berry", "sky", "teal", "forest", "bubble_gum", "violet", "cobalt", "clover", "lemon", "white"]

    def __init__(self, state: State, data: dict[str, Any]):
        self._state = state
        self.sku_id: int = int(data["sku_id"])
        self.asset = Asset._from_collectibles_nameplate(state, data["asset"])
        self.label = data["label"]
        self.palette: ValidPaletteType = data["palette"]

    @classmethod
    def _from_dict(cls, state: State, data: dict[str, Any] | None) -> Nameplate:
        if data is not None:
            return cls(state, data)
        return None

