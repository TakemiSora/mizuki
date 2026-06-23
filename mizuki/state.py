import aiohttp

from typing import TYPE_CHECKING

from mizuki.cache import CacheStorage
from mizuki.flags import IntentFlags
from mizuki.http import HTTPClient
from mizuki.gateway import GatewayClient
from mizuki.managers import (
    UserManager,
    ChannelManager,
    CommandManager,
    MessageManager,
    GuildManager
)

from mizuki.objects.command import PartialApplicationCommand

if TYPE_CHECKING:
    from mizuki.bot import Bot

class Managers:
    __slots__ = (
        "users",
        "channels",
        "commands",
        "messages",
        "guilds"
    )

    def __init__(
        self, *,
        client: HTTPClient,
        cache_storage: CacheStorage,
        application_id: int,
        commands_data: dict[str, tuple[int, PartialApplicationCommand]]
    ):
        self.users = UserManager(client, cache_storage)
        self.channels = ChannelManager(client, cache_storage)
        self.messages = MessageManager(client, cache_storage)
        self.guilds = GuildManager(client, cache_storage)

        self.commands = CommandManager(client, cache_storage, application_id, commands_data)

class ConnectionState:
    __slots__ = (
        "http",
        "gateway",
        "managers",
        "session"
    )

    def init_http(self, token: str) -> HTTPClient:
        self.http = HTTPClient()
        self.session = self.http._session = aiohttp.ClientSession(
            "https://discord.com/api/v10/",
            headers={
                "Authorization": f"Bot {token}"
            }
        )
        return self.http

    def init_managers(
        self, *,
        cache_storage: CacheStorage,
        application_id: int,
        commands_data: dict[str, tuple[int, PartialApplicationCommand]]
    ) -> Managers:
        assert hasattr(self, "http"), "Init Manager was called without init http"
        self.managers = Managers(
            client=self.http,
            cache_storage=cache_storage,
            application_id=application_id,
            commands_data=commands_data
        )
        return self.managers

    async def init_gateway(
        self, *,
        bot: Bot,
        token: str,
        intents: IntentFlags
    ) -> GatewayClient:
        assert hasattr(self, "http"), "Init Gateway was called without init http"
        self.gateway = GatewayClient(
            bot,
            self.session,
            token,
            intents
        )
        await self.gateway.connect()
        return self.gateway