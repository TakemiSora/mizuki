import aiohttp
import asyncio
from .http import State, Path
from .managers import Users
from .gateway import GatewayClient
from .flags import IntentFlags
from .errors import Unauthorized, ImproperToken

__all__ = (
    "Bot",
)

class Bot:
    __slots__ = (
        "intents",
        "_state",
        "_gateway_client",
        "users"
    )
    
    def __init__(
        self,
        intents: IntentFlags
    ):
        self.intents = intents
        self._state = State()
        self._gateway_client: GatewayClient | None = None
        self.users = Users(self._state)

    def run(self, token: str) -> None:
        asyncio.run(self.start(token))
        
    async def _verify_token(self) -> None:
        try:
            await self._state.request(Path("GET", "users/@me"))
        except Unauthorized:
            raise ImproperToken(401, "Improper token has been passed.")

    async def start(self, token: str) -> None:
        try:
            self._state.session = aiohttp.ClientSession(
                "https://discord.com/api/v10/",
                headers={
                    "Authorization": f"Bot {token}"
                }
            )
            await self._verify_token()
            self._gateway_client = GatewayClient(token, self.intents)
            await self._gateway_client.connect()
            await self._gateway_client.wait_until_closed()
        except KeyboardInterrupt:
            pass
        finally:
            await self.stop()

    async def stop(self) -> None:
        if self._gateway_client:
            await self._gateway_client.close()
        if self._state.session:
            await self._state.session.close()