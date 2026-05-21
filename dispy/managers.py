from .objects.user import User
from .objects.message import Message
from .objects.guild import Guild
from .objects.channel import parse_channel_payload
from .http import HTTPClient, Path

class BaseManager:
    __slots__ = (
        "_http"
    )

    def __init__(self, client: HTTPClient):
        self._http = client

class Users(BaseManager):
    __slots__ = ()

    async def fetch(self, user_id: int) -> User:
        return User(await self._http.request(
            Path(
                "GET",
                "users/{user_id}",
                user_id=user_id
            )
        ))

class Messages(BaseManager):
    __slots__ = ()

    async def fetch(self, channel_id: int, message_id: int):
        return Message(await self._http.request(
            Path(
                "GET",
                "channels/{channel_id}/messages/{message_id}",
                channel_id=channel_id,
                message_id=message_id
            )
        ))

class Channels(BaseManager):
    __slots__ = ()

    async def fetch(self, channel_id: int):
        return parse_channel_payload(await self._http.request(
            Path(
                "GET",
                "channels/{channel_id}",
                channel_id=channel_id
            )
        ))

class Guilds(BaseManager):
    __slots__ = ()

    async def fetch(self, guild_id: int) -> Guild:
        return Guild(await self._http.request(
            Path(
                "GET",
                "guilds/{guild_id}",
                guild_id=guild_id
            )
        ))