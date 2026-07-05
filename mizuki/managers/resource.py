from __future__ import annotations
from typing import TYPE_CHECKING

from mizuki.managers.channel import ChannelManager
from mizuki.managers.command import CommandManager
from mizuki.managers.guild import GuildManager
from mizuki.managers.message import MessageManager
from mizuki.managers.user import UserManager

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.objects.command import PartialApplicationCommand
    from mizuki.cache import CacheStorage


class Managers:
    __slots__ = ("users", "channels", "commands", "messages", "guilds")

    def __init__(
        self,
        *,
        state: ConnectionState,
        cache_storage: CacheStorage,
        application_id: int,
        commands_data: dict[str, tuple[int, PartialApplicationCommand]],
    ):
        self.users = UserManager(state, cache_storage)
        self.channels = ChannelManager(state, cache_storage)
        self.messages = MessageManager(state, cache_storage)
        self.guilds = GuildManager(state, cache_storage)

        self.commands = CommandManager(
            state, cache_storage, application_id, commands_data
        )
