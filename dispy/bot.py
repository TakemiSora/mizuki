import asyncio
import inspect
from collections.abc import Callable, Coroutine
from typing import Any

import aiohttp

from .cache import CacheSettings, CacheStorage
from .errors import ImproperToken, Unauthorized
from .flags import IntentFlags
from .gateway import GatewayClient
from .http import HTTPClient, Path
from .managers import Channels, Guilds, Messages, Users

__all__ = (
    "Bot",
)

type CoroFunc = Callable[..., Coroutine[Any, Any, Any]]

class ApplicationCommandCallbackData:
    __slots__ = (
        "description",
        "callback"
    )
    
    def __init__(self, description: str, callback: CoroFunc):
        self.description = description
        self.callback = callback

class Bot:
    __slots__ = (
        "intents",
        "http",
        "gateway",
        "_listeners",
        "_command_callbacks",
        "storage",
        "users",
        "messages",
        "channels",
        "guilds",
        "_session"
    )
    
    def __init__(
        self,
        intents: IntentFlags,
        cache_settings: CacheSettings | None = None
    ):
        self.intents = intents
        self.http = HTTPClient()
        self.gateway: GatewayClient | None = None
        self._listeners: dict[str, list[CoroFunc]] = {}
        self._command_callbacks: dict[str, ApplicationCommandCallbackData] = {}

        self.storage = CacheStorage(cache_settings or CacheSettings())
        self.users = Users(self.http, self.storage)
        self.messages = Messages(self.http, self.storage)
        self.channels = Channels(self.http, self.storage)
        self.guilds = Guilds(self.http, self.storage)
        
        self._session: aiohttp.ClientSession | None = None

    def run(self, token: str) -> None:
        asyncio.run(self.start(token))
        
    async def _verify_token(self) -> None:
        try:
            await self.http.request(Path("GET", "users/@me"))
        except Unauthorized:
            raise ImproperToken(401, "Improper token has been passed.")

    async def start(self, token: str) -> None:
        try:
            if self.storage.settings.cache_invalidation: self.storage.start_cleanup_tasks()
            self._session = aiohttp.ClientSession(
                "https://discord.com/api/v10/",
                headers={
                    "Authorization": f"Bot {token}"
                }
            )
            self.http._session = self._session
            await self._verify_token()
            self.gateway = GatewayClient(self, self._session, token, self.intents)
            await self.gateway.connect()
            await self.gateway.wait_until_closed()
        except asyncio.CancelledError:
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        try:
            if self.gateway:
                await self.gateway.close()
        finally:
            if self._session:
                await self._session.close()

    def listen(self, name: str | None = None):
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func): raise TypeError(f"Event listener '{func.__name__}' has to be a coroutine function.")
            self._listeners.setdefault(name or func.__name__, []).append(func)
            return func
        return decorator
        
    def command(self, *, name: str, description: str):
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func): raise TypeError(f"Command callback for '{name}:{func.__name__}' has to be a coroutine function.")
            self._command_callbacks[name] = ApplicationCommandCallbackData(description, func)
            return func
        return decorator