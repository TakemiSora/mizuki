from __future__ import annotations
from typing import Any
from .asset import Asset
from .state import State

class AvatarDecoration:
    def __init__(self, state: State, data: dict[str, Any]):
        self._state = state

        self.sku_id: int = int(data["sku_id"])
        self.asset = Asset._from_user_avatar_decoration(state, data["asset"])

    @classmethod
    def _from_dict(cls, state: State, data: dict[str, Any] | None) -> AvatarDecoration | None:
        if data is not None:
            return cls(state, data)
        return None
