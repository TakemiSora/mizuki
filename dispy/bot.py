import aiohttp
from .http import State
from .managers import Users

class Bot:
    def __init__(
        self,
        token: str
    ):
        self.token = token
        self._state = State()
        self.users = Users()

    async def connect(self) -> None:
        self._state.session = aiohttp.ClientSession(
            "https://discord.com/api/v10/",
            headers={
                "Authorization": f"Bot {self.token}"
            }
        )

    async def close(self) -> None:
        if self._state.session is not None:
            await self._state.session.close()
