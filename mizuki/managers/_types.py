from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.cache import CacheStorage


class BaseManager:
    __slots__ = ("_state", "_cache_storage")

    def __init__(self, state: ConnectionState, cache: CacheStorage):
        self._state = state
        self._cache_storage = cache
