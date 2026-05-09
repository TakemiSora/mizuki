from __future__ import annotations
from typing import Any
from .state import State

class UserPrimaryGuild:
    def __init__(self, state: State, data: dict[str, Any]):
        self._state = state

        self.id = data.get("identity_guild_id")

    @classmethod
    def _from_dict(cls, state: State, data: dict[str, Any] | None) -> UserPrimaryGuild | None:
        if data is not None:
            return cls(state, data)
        return None
