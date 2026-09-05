from __future__ import annotations

from typing import TYPE_CHECKING

from mizuki.managers.channel import ChannelManager
from mizuki.managers.command import CommandManager
from mizuki.managers.guild import GuildManager
from mizuki.managers.message import MessageManager
from mizuki.managers.role import RoleManager
from mizuki.managers.user import UserManager

if TYPE_CHECKING:
    from mizuki.cache import CacheStorage
    from mizuki.objects.command import (
        PartialApplicationCommand,
        PartialApplicationCommandGroup,
    )
    from mizuki.state import ConnectionState


class Managers:
    __slots__ = ("channels", "commands", "guilds", "messages", "roles", "users")

    def __init__(
        self,
        *,
        state: ConnectionState,
        cache_storage: CacheStorage,
        application_id: int,
        commands_data: dict[
            str, tuple[int, PartialApplicationCommand | PartialApplicationCommandGroup]
        ],
    ) -> None:
        self.users = UserManager(state, cache_storage)
        self.channels = ChannelManager(state, cache_storage)
        self.messages = MessageManager(state, cache_storage)
        self.roles = RoleManager(state, cache_storage)
        self.guilds = GuildManager(state, cache_storage)

        self.commands = CommandManager(
            state, cache_storage, application_id, commands_data
        )
