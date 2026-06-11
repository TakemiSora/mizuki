from __future__ import annotations
import asyncio
import logging
from typing import Any, TYPE_CHECKING

from .objects.command import ApplicationCommandOption

from .enums.channel import ChannelType
from .enums.command import CommandOptionType
from .enums.interaction import InteractionType
from .objects.channel import ThreadChannel, ThreadMember, parse_channel_payload
from .objects.guild import Guild, UnavailableGuild, parse_guild_payload
from .objects.interaction import Interaction, ResolvedData, InvokedApplicationCommandOption
from .payloads.channel import (
    GuildChannelPayload,
    PrivateChannelPayload,
    ThreadCreatePayload,
    ThreadDeletePayload,
    ThreadPayload,
)
from .payloads.guild import GuildPayload, UnavailableGuildPayload
from .payloads.interaction import InteractionPayload
from ._utils import scls

if TYPE_CHECKING:
    from .bot import Bot

_log = logging.getLogger(__name__)

class EventDispatcher:
    __slots__ = (
        "_dispatch_handlers",
        "bot"
    )

    def __init__(self, bot: Bot):
        self.bot = bot
        self._dispatch_handlers = {
            # GUILDS 
                "GUILD_CREATE": self._handle_guild_create,
                "GUILD_UPDATE": self._handle_guild_update,
                "GUILD_DELETE": self._handle_guild_delete,
                "CHANNEL_CREATE": self._handle_channel_create,
                "CHANNEL_UPDATE": self._handle_channel_update,
                "CHANNEL_DELETE": self._handle_channel_delete,
                "THREAD_CREATE": self._handle_thread_create,
                "THREAD_UPDATE": self._handle_thread_update,
                "THREAD_DELETE": self._handle_thread_delete,
            "INTERACTION_CREATE": self._handle_interaction_create,
            "READY": self._handle_ready
        }

    def _on_task_done(self, task: asyncio.Task, data: str):
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            _log.error("%s failed with exception", data, exc_info=exc)

    async def _dispatch(self, key: str, *args: Any):
        for f in self.bot._listeners.get(key, []):
            asyncio.create_task(f(*args)).add_done_callback(lambda t: self._on_task_done(t, f"Function {f.__name__} listening to '{key}'"))
            _log.debug("Dispatched %s to function '%s'.", key, f.__name__)
            
    def _parse_option_value(self, resolved: ResolvedData, option: InvokedApplicationCommandOption) -> Any:
        match option.type:
            case CommandOptionType.CHANNEL:
                assert isinstance(option.value, str)
                value = resolved.channels[int(option.value)]
                
            case CommandOptionType.ROLE:
                assert isinstance(option.value, str)
                value = resolved.roles[int(option.value)]
            
            case CommandOptionType.USER:
                assert isinstance(option.value, str)
                
                if (m := resolved.members.get(int(option.value))) is not None:
                    value = m
                else:
                    value = resolved.users[int(option.value)]
                    
            case CommandOptionType.MENTIONABLE:
                assert isinstance(option.value, str)
                val = int(option.value)
                if (r := resolved.roles.get(val)) is not None:
                    value = r
                else:
                    if (m := resolved.members.get(val)) is not None:
                        value = m
                    else:
                        value = resolved.users[val]
                        
            case _:
                value = None
                
        return value or option.value
        
    
    def _parse_options(self, command_options: dict[str, ApplicationCommandOption], resolved: ResolvedData, options: list[InvokedApplicationCommandOption]) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        display_to_callback_keys: dict[str, str] = {o.name: p for p, o in command_options.items()}
        
        for option in options:
            kwargs[display_to_callback_keys.get(option.name, option.name)] = self._parse_option_value(resolved, option)
            #                      ^^^^^^^^^^^^^^^^^^^
            #   Attempts to fjnd correct CallbackParameterName, if not defaults to DisplayParameterName
        return kwargs
            
    async def _dispatch_commands(self, name: str, interaction: Interaction):
        command_data = self.bot._commands_data.get(name)
        callback = command_data[1]._callback if command_data else None
        if callback and command_data:
            assert interaction.type is InteractionType.APPLICATION_COMMAND and interaction.data is not None
            kwargs = self._parse_options(
                getattr(callback, "__command_options__", {}),
                interaction.data.resolved,
                interaction.data.options
            ) if interaction.data.resolved else {}
            task = asyncio.create_task(callback(interaction, **kwargs))
            task.add_done_callback(lambda t: self._on_task_done(t, f"Handler Function {callback.__name__} for command '{name}'"))
            _log.debug("Command %s (func=%s) dispatched.", name, callback.__name__)
        else:
            _log.warning("Recieved command %s, but no handler was found for it.", name)
            
    async def _handle_guild_create(self, data: GuildPayload | UnavailableGuildPayload):
        guild = self.bot._storage.update_guilds(g) if isinstance((g := parse_guild_payload(data)), Guild) else g
        await self._dispatch("on_guild_create", guild)
        
    async def _handle_guild_update(self, data: GuildPayload):
        guild = self.bot._storage.update_guilds(Guild(data))
        await self._dispatch("on_guild_update", guild)
    
    async def _handle_guild_delete(self, data: UnavailableGuildPayload):
        guild = UnavailableGuild(data)
        kicked = not guild.unavailable
        await self._dispatch("on_guild_delete", guild, kicked)

    async def _handle_channel_create(self, data: GuildChannelPayload | PrivateChannelPayload):
        channel = self.bot._storage.update_channels(parse_channel_payload(data))
        await self._dispatch("on_channel_create", channel)

    async def _handle_channel_update(self, data: GuildChannelPayload | PrivateChannelPayload):
        channel = self.bot._storage.update_channels(parse_channel_payload(data))
        await self._dispatch("on_channel_update", channel)

    async def _handle_channel_delete(self, data: GuildChannelPayload | PrivateChannelPayload):
        channel = self.bot._storage.remove_channel(int(data["id"]))
        await self._dispatch("on_channel_delete", channel or parse_channel_payload(data))

    async def _handle_thread_create(self, data: ThreadCreatePayload):
        newly_created = data.get("newly_created", False)
        thread_member = scls(ThreadMember, data.get("member"))
        channel = self.bot._storage.update_channels(ThreadChannel(data))
        await self._dispatch("on_thread_create", channel, newly_created, thread_member)

    async def _handle_thread_update(self, data: ThreadPayload):
        channel = self.bot._storage.update_channels(ThreadChannel(data))
        await self._dispatch("on_thread_update", channel)

    async def _handle_thread_delete(self, data: ThreadDeletePayload):
        id = int(data["id"])
        guild_id = int(data["guild_id"])
        parent_id = int(data["parent_id"])
        type = ChannelType(data["type"])
        self.bot._storage.remove_channel(id)
        await self._dispatch("on_thread_delete", id, guild_id, parent_id, type)
        
    async def _handle_interaction_create(self, data: InteractionPayload):
        guild = self.bot.guilds.get(int(g)) if (g := data.get("guild_id")) else None
        interaction = Interaction(self.bot.http, data, guild=guild)
        match interaction.type:
            case InteractionType.APPLICATION_COMMAND:
                if interaction.data: await self._dispatch_commands(interaction.data.name, interaction)

        await self._dispatch("on_interaction_create", interaction)

    async def _handle_ready(self, _):
        await self._dispatch("on_ready")