import aiohttp
import asyncio
from typing import Any
from urllib.parse import quote
from .errors import NotFound, HTTPException, Forbidden, Unauthorized

class Path:
    __slots__ = (
        "method",
        "url",
        "channel_id",
        "guild_id",
        "webhook_id",
        "webhook_token"
    )
    
    def __init__(self, method: str, url: str, **parameters):
        self.method = method
        if parameters:
            self.url = url.format_map({key: quote(val, safe = "") if isinstance(val, str) else val for key, val in parameters.items()})
        else:
            self.url = url

        self.channel_id = parameters.get("channel_id")
        self.guild_id = parameters.get("guild_id")
        self.webhook_id = parameters.get("webhook_id")
        self.webhook_token = parameters.get("webhook_token")

    @property
    def route_key(self) -> str:
        return f"{self.method}:{self.url}+{"+".join(str(val) for val in [self.channel_id, self.guild_id, self.webhook_id, self.webhook_token])}"

class RateLimitBucket:
    __slots__ = (
        "remaining",
        "reset_after",
        "lock"
    )
    
    def __init__(self, remaining: int, reset_after: float):
        self.remaining = remaining
        self.reset_after = reset_after
        self.lock = asyncio.Lock()

    def update_bucket(self, resp: aiohttp.ClientResponse) -> None:
        headers = resp.headers

        self.remaining = int(headers.get("X-RateLimit-Remaining", 0))
        self.reset_after = float(headers.get("X-RateLimit-Reset-After", 0.1))

class State:
    __slots__ = (
        "session",
        "_global_ratelimit",
        "_buckets_keys",
        "_buckets"
    )
    
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None

        self._global_ratelimit = asyncio.Event()
        self._global_ratelimit.set()
        self._buckets_keys: dict[str, str] = {}
        self._buckets: dict[str, RateLimitBucket] = {}
        
    async def request(self, path: Path, **kwargs: Any) -> Any:
        await self._global_ratelimit.wait()
        
        bucket_id = self._buckets_keys.get(path.route_key)
        bucket = self._buckets.get(bucket_id) if bucket_id else None

        async with (bucket.lock if bucket else asyncio.Lock()):
            assert self.session is not None, "Cannot call session without intializing first."
                
            async with self.session.request(path.method, path.url, **kwargs) as resp:
                new_bucket_id = resp.headers.get("X-RateLimit-Bucket")

                if new_bucket_id is not None:
                    if new_bucket_id not in self._buckets:
                        self._buckets[new_bucket_id] = RateLimitBucket(1, 0)
                    self._buckets[new_bucket_id].update_bucket(resp)
                    self._buckets_keys[path.route_key] = new_bucket_id

                if resp.status == 429:
                    data = await resp.json()
                    retry_after = float(data["retry_after"])
                    limit_scope = resp.headers.get("X-RateLimit-Scope")

                    if limit_scope == "global":
                        self._global_ratelimit.clear()
                        await asyncio.sleep(retry_after)
                        self._global_ratelimit.set()
                    else:
                        await asyncio.sleep(retry_after)

                    return await self.request(path, **kwargs)
                
                if resp.status >= 400:
                    data = await resp.json()
                    message = data.get("message", "")
                    match resp.status:
                        case 401: raise Unauthorized(resp.status, message)
                        case 403: raise Forbidden(resp.status, message)
                        case 404: raise NotFound(resp.status, message)
                        case _: raise HTTPException(resp.status, message)

                if new_bucket_id:
                    bucket = self._buckets.get(new_bucket_id)
                    if bucket and bucket.remaining == 0:
                        await asyncio.sleep(bucket.reset_after)

                return await resp.json()
