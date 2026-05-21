import aiohttp
import asyncio
from .http import HTTPClient, Path
from .managers import Users, Messages, Channels, Guilds
from .gateway import GatewayClient
from .flags import IntentFlags
from .objects.errors import Unauthorized, ImproperToken

__all__ = (
    "Bot",
)

class Bot:
    __slots__ = (
        "intents",
        "http",
        "gateway",
        "users",
        "messages",
        "channels",
        "guilds"
    )
    
    def __init__(
        self,
        intents: IntentFlags
    ):
        self.intents = intents
        self.http = HTTPClient()
        self.gateway: GatewayClient | None = None
        self.users = Users(self.http)
        self.messages = Messages(self.http)
        self.channels = Channels(self.http)
        self.guilds = Guilds(self.http)

    def run(self, token: str) -> None:
        asyncio.run(self.start(token))
        
    async def _verify_token(self) -> None:
        try:
            await self.http.request(Path("GET", "users/@me"))
        except Unauthorized:
            raise ImproperToken(401, "Improper token has been passed.")

    async def start(self, token: str) -> None:
        try:
            session = aiohttp.ClientSession(
                "https://discord.com/api/v10/",
                headers={
                    "Authorization": f"Bot {token}"
                }
            )
            self.http._session = session
            await self._verify_token()
            self.gateway = GatewayClient(session, token, self.intents)
            await self.gateway.connect()
            await self.gateway.wait_until_closed()
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    async def stop(self) -> None:
        if self.gateway:
            await self.gateway.close()
        if self.http._session:
            await self.http._session.close()
