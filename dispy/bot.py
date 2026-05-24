import aiohttp
import asyncio
from .http import HTTPClient, Path
from .managers import Users, Messages, Channels, Guilds
from .gateway import GatewayClient
from .flags import IntentFlags
from .errors import Unauthorized, ImproperToken
from .cache import CacheSettings, CacheStorage
from typing import Callable, Coroutine

__all__ = (
    "Bot",
)

CoroFunc = Callable[..., Coroutine]

class Bot:
    __slots__ = (
        "intents",
        "http",
        "gateway",
        "_listeners",
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
            pass
        finally:
            await self.stop()

    async def stop(self) -> None:
        if self.gateway:
            await self.gateway.close()
        if self._session:
            await self._session.close()

    def listen(self, name: str | None = None):
        def decorator(func: CoroFunc) -> CoroFunc:
            self._listeners.setdefault(name or func.__name__, []).append(func)
            return func
        return decorator