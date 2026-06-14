import aiohttp
import asyncio
import logging
from typing import Any
from json import dumps
from contextlib import ExitStack
from urllib.parse import quote
from .file import File
from .errors import NotFound, HTTPException, Forbidden, Unauthorized, _RateLimitedRetry
from ._utils import _MISSING

_log  = logging.getLogger(__name__)

class Path:
    """
    The Path/URL metadata for a HTTP Request. Parameters should be initalized with keyword arguments rather than f-strings.
    
    Parameters
    ----------
    method : :class:`str`
        The HTTP Method for the request such as ``GET``, ``POST``.
    url : :class:`str`
        The URL endpoint to make the request to. Refer to examples below for formatting.
    **parameters : :class:`Any <typing.Any>`
        The Parameters for the URL. Refer at examples below for formatting.
        
    Examples
    --------
    
    .. code-block:: python
    
        mizuki.Path(
            "GET",
            "channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id
        )))
    """
    
    method: str
    "The HTTP Method for the request such as ``GET``, ``POST``."
    
    url: str
    "The formatted URL endpoint to make the request to."

    channel_id: str | None
    ":meta private:"

    guild_id: str | None
    ":meta private:"

    webhook_id: str | None
    ":meta private:"

    webhook_token: str | None
    ":meta private:"
    
    __slots__ = (
        "method",
        "url",
        "channel_id",
        "guild_id",
        "webhook_id",
        "webhook_token"
    )
    
    def __init__(self, method: str, url: str, **parameters: Any):
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
    def _route_key(self) -> str:
        return f"{self.method}:{self.url}+{"+".join(str(val) for val in [self.channel_id, self.guild_id, self.webhook_id, self.webhook_token])}"

class RateLimitBucket:
    ":meta private:"
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

        self.remaining = int(headers.get("X-RateLimit-Remaining", 1))
        self.reset_after = float(headers.get("X-RateLimit-Reset-After", 0.1))

class HTTPClient:
    """
    The Client that is used to interact with the Discord REST API. This should **not** be constructed by the user.
    """
    __slots__ = (
        "_session",
        "_global_ratelimit",
        "_buckets_keys",
        "_buckets"
    )
    
    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

        self._global_ratelimit = asyncio.Event()
        self._global_ratelimit.set()
        self._buckets_keys: dict[str, str] = {}
        self._buckets: dict[str, RateLimitBucket] = {}
        
    async def _request(self, path: Path, **kwargs: Any) -> Any:
        await self._global_ratelimit.wait()
        
        _log.debug("Attempting to make request %s: %s", path.method, path.url)
        
        bucket_id = self._buckets_keys.get(path._route_key)
        bucket = self._buckets.get(bucket_id) if bucket_id else None

        try:
            async with (bucket.lock if bucket else asyncio.Lock()):
                assert self._session is not None, "Cannot call session without intializing first."
                    
                async with self._session.request(path.method, path.url, **kwargs) as resp:
                    new_bucket_id = resp.headers.get("X-RateLimit-Bucket")

                    if new_bucket_id is not None:
                        if new_bucket_id not in self._buckets:
                            self._buckets[new_bucket_id] = RateLimitBucket(1, 0)
                        self._buckets[new_bucket_id].update_bucket(resp)
                        self._buckets_keys[path._route_key] = new_bucket_id

                    if resp.status == 429:
                        data = await resp.json()
                        retry_after = float(data["retry_after"])
                        limit_scope = resp.headers.get("X-RateLimit-Scope")

                        raise _RateLimitedRetry(data, retry_after, limit_scope, new_bucket_id or bucket_id)
                    
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
                            _log.debug("Pre-emptively waiting for bucket reset on BucketID = %s on URL = %s. Continuing in %.2f seconds.", new_bucket_id, path.url, bucket.reset_after)
                            await asyncio.sleep(bucket.reset_after)
                    
                    if "application/json" in resp.headers.get("Content-Type", ""): return await resp.json()

        except _RateLimitedRetry as e:
            if e.limit_scope == "global":
                self._global_ratelimit.clear()
                _log.warning("Hit the global ratelimit for the REST API. Continuing in %.2f seconds", e.retry_after)
                await asyncio.sleep(e.retry_after)
                self._global_ratelimit.set()
            else:
                _log.warning("Hit the ratelimit when accessing BucketID = %s on URL = %s. Continuing in %.2f seconds.", e.bucket_id, path.url, e.retry_after)
                await asyncio.sleep(e.retry_after)

            return await self._request(path, **kwargs)

    async def request(
        self, path: Path, *,
        files: list[File] = _MISSING,
        json: dict[str, Any] = _MISSING,
        **kwargs: Any
    ) -> Any:
        """
        Used to make a HTTP request to the Discord API.

        Parameters
        ----------
        path : :class:`Path <mizuki.http.Path>`
            The Path metadata for the request.
            
        files : list[:class:`File` <mizuki.file.File>`], optional
            The files to upload with the request. Providing this field makes the request use ``multipart/form-data``.
            
        json : dict[:class:`str`, :class:`Any <typing.Any>`], optional
            The JSON payload for the request, is added under ``payload_json`` in the FormData if files is also provided.
            
        **kwargs : :class:`Any <typing.Any>`
            The keyword arguments for the request. These are passed directly to :meth:`aiohttp.ClientSession.request()` method.

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.
            
        :class:`Forbidden`
            You are forbidden from accessing this endpoint.
            
        :class:`NotFound`
            The resource you tried to request wasn't found.
            
        :class:`HTTPException`
            An HTTP error occured.
        """
        request_data = {}

        with ExitStack() as stack:
            if files: 
                request_data["data"] = data = aiohttp.FormData()

                for i, file in enumerate(files):
                    file_bytes = stack.enter_context(open(file.path, "rb"))
                    data.add_field(
                        f"files[{i}]",
                        file_bytes,
                        filename=file.filename
                    )

                data.add_field(
                    "payload_json",
                    dumps(json)
                )

            elif json and not files:
                 request_data["json"] = json

            return await self._request(
                path,
                **request_data,
                **kwargs
            )