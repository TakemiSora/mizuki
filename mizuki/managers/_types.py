from ..http import HTTPClient
from ..cache import CacheStorage

class BaseManager:
    __slots__ = (
        "_http",
        "_cache_storage"
    )

    def __init__(self, client: HTTPClient, cache: CacheStorage):
        self._http = client
        self._cache_storage = cache