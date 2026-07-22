from __future__ import annotations
import asyncio
import logging

from typing import Any, TYPE_CHECKING

from mizuki._utils import scls

from mizuki.enums.channel import ChannelType
from mizuki.enums.command import CommandOptionType
from mizuki.enums.interaction import InteractionType
from mizuki.objects.command import ApplicationCommandOption
from mizuki.objects.channel import ThreadChannel, ThreadMember, parse_channel_payload
from mizuki.objects.components.common import BaseComponentResponse
from mizuki.objects.guild import Guild, UnavailableGuild, parse_guild_payload
from mizuki.objects.interaction import (
    Interaction,
    InvokedApplicationCommand,
    InvokedApplicationCommandOption,
    ResolvedData,
)

if TYPE_CHECKING:
    from mizuki.bot import Bot

    from mizuki.payloads.guild import GuildPayload, UnavailableGuildPayload
    from mizuki.payloads.interaction import InteractionPayload
    from mizuki.payloads.channel import (
        GuildChannelPayload,
        PrivateChannelPayload,
        ThreadCreatePayload,
        ThreadDeletePayload,
        ThreadPayload,
    )

_log = logging.getLogger(__name__)


class EventDispatcher:
    __slots__ = ("_dispatch_handlers", "_interaction_dispatchers", "bot")

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
            "READY": self._handle_ready,
        }

        self._interaction_dispatchers = {
            InteractionType.APPLICATION_COMMAND: self._dispatch_commands,
            InteractionType.MESSAGE_COMPONENT: self._dispatch_components,
        }

    def _on_task_done(self, task: asyncio.Task, data: str):
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            _log.error("%s failed with exception", data, exc_info=exc)

    async def _dispatch(self, key: str, *args: Any):
        for f in self.bot._listeners.get(key, []):
            asyncio.create_task(f(*args)).add_done_callback(
                lambda t: self._on_task_done(
                    t, f"Function {f.__name__} listening to '{key}'"
                )
            )
            _log.debug("Dispatched %s to function '%s'.", key, f.__name__)

    def _parse_option_value(
        self, resolved: ResolvedData, option: InvokedApplicationCommandOption
    ) -> Any:
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

    def _parse_options(
        self,
        command_options: dict[str, ApplicationCommandOption],
        resolved: ResolvedData,
        options: list[InvokedApplicationCommandOption],
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        display_to_callback_keys: dict[str, str] = {
            o.name: p for p, o in command_options.items()
        }

        for option in options:
            kwargs[display_to_callback_keys.get(option.name, option.name)] = (
                self._parse_option_value(resolved, option)
            )
            #                      ^^^^^^^^^^^^^^^^^^^
            #   Attempts to fjnd correct CallbackParameterName, if not defaults to DisplayParameterName
        return kwargs

    async def _dispatch_commands(self, interaction: Interaction):
        assert isinstance(interaction.data, InvokedApplicationCommand)

        command_data = self.bot._commands_data.get(interaction.data.name)
        callback = command_data[1]._callback if command_data else None
        if callback and command_data:
            kwargs = (
                self._parse_options(
                    getattr(callback, "__command_options__", {}),
                    interaction.data.resolved,
                    interaction.data.options,
                )
                if interaction.data.resolved
                else {}
            )

            asyncio.create_task(callback(interaction, **kwargs)).add_done_callback(
                lambda t: self._on_task_done(
                    t,
                    f"Handler Function {callback.__name__} for command '{interaction.data.name}'",  # type: ignore # This is resolved
                )
            )
            _log.debug(
                "Command %s (func=%s) dispatched.",
                interaction.data.name,
                callback.__name__,
            )
        else:
            _log.warning(
                "Recieved command %s, but no handler was found for it.",
                interaction.data.name,
            )

    async def _dispatch_components(self, interaction: Interaction):
        assert isinstance(interaction.data, BaseComponentResponse)

        component_type_val = interaction.data.component_type.value

        try:
            callback = self.bot._state.components_data[interaction.data.custom_id]

            asyncio.create_task(
                callback(interaction, interaction.data)
            ).add_done_callback(
                lambda t: self._on_task_done(
                    t,
                    f"Component Interaction Callback (ComponentType={component_type_val}, Func={callback.__name__})",
                )
            )

            _log.debug(
                f"Dispatched component callback (ComponentType={component_type_val}, Func={callback.__name__})"
            )
        except KeyError:
            _log.warning(
                "Recieved component interaction (ComponentType=%s), but no callback was found for it.",
                component_type_val,
            )

    async def _handle_guild_create(self, data: GuildPayload | UnavailableGuildPayload):
        guild = (
            self.bot._storage.update_guilds(g)
            if isinstance(
                (g := parse_guild_payload(data, state=self.bot._state)), Guild
            )
            else g
        )
        await self._dispatch("on_guild_create", guild)

    async def _handle_guild_update(self, data: GuildPayload):
        guild = self.bot._storage.update_guilds(Guild(data, state=self.bot._state))
        await self._dispatch("on_guild_update", guild)

    async def _handle_guild_delete(self, data: UnavailableGuildPayload):
        guild = UnavailableGuild(data)
        kicked = not guild.unavailable
        await self._dispatch("on_guild_delete", guild, kicked)

    async def _handle_channel_create(
        self, data: GuildChannelPayload | PrivateChannelPayload
    ):
        channel = self.bot._storage.update_channels(
            parse_channel_payload(data, state=self.bot._state)
        )
        await self._dispatch("on_channel_create", channel)

    async def _handle_channel_update(
        self, data: GuildChannelPayload | PrivateChannelPayload
    ):
        channel = self.bot._storage.update_channels(
            parse_channel_payload(data, state=self.bot._state)
        )
        await self._dispatch("on_channel_update", channel)

    async def _handle_channel_delete(
        self, data: GuildChannelPayload | PrivateChannelPayload
    ):
        channel = self.bot._storage.remove_channel(int(data["id"]))
        await self._dispatch(
            "on_channel_delete",
            channel or parse_channel_payload(data, state=self.bot._state),
        )

    async def _handle_thread_create(self, data: ThreadCreatePayload):
        newly_created = data.get("newly_created", False)
        thread_member = scls(ThreadMember, data.get("member"), state=self.bot._state)
        channel = self.bot._storage.update_channels(
            ThreadChannel(data, state=self.bot._state)
        )
        await self._dispatch("on_thread_create", channel, newly_created, thread_member)

    async def _handle_thread_update(self, data: ThreadPayload):
        channel = self.bot._storage.update_channels(
            ThreadChannel(data, state=self.bot._state)
        )
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
        interaction = Interaction(data, guild=guild, state=self.bot._state)

        if dispatcher := self._interaction_dispatchers.get(interaction.type):
            await dispatcher(interaction)

        await self._dispatch("on_interaction_create", interaction)

    async def _handle_ready(self, _):
        await self._dispatch("on_ready")
