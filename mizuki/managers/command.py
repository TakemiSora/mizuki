from __future__ import annotations
from typing import Any, overload, TYPE_CHECKING

from mizuki.http import Path
from mizuki.cache import CacheStorage
from mizuki._utils import _MISSING, assign_val_dict, mtd

from mizuki.managers._types import BaseManager
from mizuki.objects.command import (
    ApplicationCommandOption,
    Localization,
    ApplicationCommand,
    PartialApplicationCommand,
)
from mizuki.objects.permissions import Permissions
from mizuki.enums.interaction import InteractionContextType, ApplicationIntegrationType

if TYPE_CHECKING:
    from mizuki.state import ConnectionState


class CommandManager(BaseManager):
    """
    Manager used to manage :class:`~mizuki.objects.command.ApplicationCommand`.
    """

    __slots__ = ("_application_id", "_commands_data")

    def __init__(
        self,
        state: ConnectionState,
        storage: CacheStorage,
        application_id: int,
        commands_data: dict[str, tuple[int, PartialApplicationCommand]],
    ):
        super().__init__(state, storage)
        self._application_id = application_id
        self._commands_data = commands_data

    async def _command_request(
        self,
        *,
        method: str,
        command_id: int | None = None,
        guild_id: int | None = None,
        **kwargs: Any,
    ) -> Any:
        return await self._state.http.request(
            Path(
                method,
                "applications/{application_id}{guild_or_not}/commands{command_suffix}",
                application_id=self._application_id,
                guild_or_not=f"/guilds/{guild_id}" if guild_id is not None else "",
                command_suffix=f"/{command_id}" if command_id is not None else "",
            ),
            **kwargs,
        )

    async def fetch_all(
        self, *, guild_id: int | None = None, with_localizations: bool = True
    ) -> list[ApplicationCommand]:
        """
        Fetches a list of all application commands from the Discord API.

        Parameters
        ----------
        guild_id : :class:`int`, optional
            The guild ID for fetching commands scoped by guild.

        with_localizations : :class:`bool`, optional
            Whether :attr:`~mizuki.objects.command.ApplicationCommand.name_localizations` and :attr:`~mizuki.objects.command.ApplicationCommand.description_localizations` should be fetched. Defaults to ``True``.

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_commands_bulk(
            [
                ApplicationCommand(c)
                for c in await self._command_request(
                    method="GET",
                    guild_id=guild_id,
                    params={"with_localizations": str(with_localizations).lower()},
                )
            ],
            guild_id=guild_id or 0,
        )

    def get_all(self, *, guild_id: int | None = None) -> list[ApplicationCommand]:
        """
        Gets a list of ApplicationCommand frok the internal cache. Can be empty if the commands are not fetched atleast once.

        Parameters
        ----------
        guild_id : :class:`int`
            The Guild ID of the Guild for getting commands scoped by guild.
        """
        return self._cache_storage.get_all_commands(guild_id=guild_id or 0)

    async def add(
        self, command: PartialApplicationCommand, *, guild_id: int | None = None
    ) -> ApplicationCommand:
        """
        Adds a specific command object to the Application.

        Parameters
        ----------
        command : :class:`~mizuki.objects.command.PartialApplicationCommand`
            The command to sync.

        guild_id : :class:`int`, optional
            The Guild ID to add to if scoped by guild.

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_command(
            ApplicationCommand(
                await self._command_request(
                    method="POST", json=command._to_dict(), guild_id=guild_id
                )
            ),
            guild_id=guild_id or 0,
        )

    async def fetch(
        self, command_id: int, *, guild_id: int | None = None
    ) -> ApplicationCommand:
        """
        Fetches an application command from the Discord API.

        Parameters
        ----------
        command_id : :class:`int`
            The ID of the command to fetch.

        guild_id : :class:`int`, optional
            The Guild ID for fetching commands if scoped by guild.

        Raises
        ------
        :class:`NotFound`
            The command you tried to fetch does not exist.

        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_command(
            ApplicationCommand(
                await self._command_request(
                    method="GET", guild_id=guild_id, command_id=command_id
                )
            ),
            guild_id=guild_id or 0,
        )

    async def sync_all(self) -> list[ApplicationCommand]:
        """
        Syncs registered commands via :meth:`@Bot.command() <mizuki.objects.bot.Bot.command>` to the Application. This will **override** all commands currently synced.

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        global_cmds: list[PartialApplicationCommand] = []
        guild_cmds: dict[int, list[PartialApplicationCommand]] = {}

        for data in self._commands_data.values():
            id = data[0]

            if id == 0:
                global_cmds.append(data[1])
            else:
                if id not in guild_cmds:
                    guild_cmds[id] = []
                guild_cmds[id].append(data[1])

        to_return: list[ApplicationCommand] = []
        if global_cmds:
            to_return += await self.sync_bulk(global_cmds)

        for guild_id, cmds in guild_cmds.items():
            to_return += await self.sync_bulk(cmds, guild_id=guild_id)

        return to_return

    async def sync_bulk(
        self, commands: list[PartialApplicationCommand], *, guild_id: int | None = None
    ) -> list[ApplicationCommand]:
        """
        Syncs given commands to the Application. This will **override** all commands currently synced.

        Parameters
        ----------
        commands : list[:class:`~mizuki.objects.command.PartialApplicationCommand`]
            The new list of commands.

        guild_id : :class:`int`, optional
            The Guild ID of the Guild to PUT to if scoped by guild.

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_commands_bulk(
            [
                ApplicationCommand(c)
                for c in await self._command_request(
                    method="PUT",
                    guild_id=guild_id,
                    json=[c._to_dict() for c in commands],
                )
            ],
            guild_id=guild_id or 0,
        )

    @overload
    async def edit(
        self,
        command_id: int,
        *,
        guild_id: int,
        name: str = _MISSING,
        name_localizations: Localization | None = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization | None = _MISSING,
        options: list[ApplicationCommandOption] = _MISSING,
        default_member_permissions: Permissions | None = _MISSING,
        nsfw: bool = _MISSING,
    ) -> ApplicationCommand: ...

    @overload
    async def edit(
        self,
        command_id: int,
        *,
        name: str = _MISSING,
        name_localizations: Localization | None = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization | None = _MISSING,
        options: list[ApplicationCommandOption] = _MISSING,
        default_member_permissions: Permissions | None = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = _MISSING,
    ) -> ApplicationCommand: ...

    async def edit(
        self,
        command_id: int,
        *,
        guild_id: int | None = None,
        name: str = _MISSING,
        name_localizations: Localization | None = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization | None = _MISSING,
        options: list[ApplicationCommandOption] = _MISSING,
        default_member_permissions: Permissions | None = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = _MISSING,
    ) -> ApplicationCommand:
        """
        Edits an application command. All parameters to this method besides ``command_id`` are optional.

        Parameters
        ----------
        command_id : :class:`int`
            The ID of the command to edit.

        guild_id : :class:`int`
            The Guild ID of the Guild, if editing command scoped by guild.

        name : :class:`str`
            The name of the command.

        name_localizations : :class:`~mizuki.objects.command.Localization`
            The localizations for the name of the command.

        description : :class:`str`
            The description of the command.

        description_localizations : :class:`~mizuki.objects.command.Localization`
            The localizations for the description of the command.

        options : list[:class:`~mizuki.objects.command.ApplicationCommandOption`]
            The options (parameters or sub-commands) of the command.

        default_member_permissions : :class:`~mizuki.objects.permissions.Permissions`
            The default member permissions of the command.

        integration_types : list[:class:`~mizuki.enums.interaction.ApplicationIntegrationType`]
            The installation contexts where the command is available.

        contexts : list[:class:`~mizuki.enums.interaction.InteractionContextType`]
            The installation contexts where the command can be used.

        nsfw : :class:`bool`
            Whether the command is NSFW.

        Raises
        ------
        :class:`NotFound`
            The command you tried to edit does not exist.

        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """

        payload = assign_val_dict(
            {},
            _MISSING,
            name=name,
            name_localizations=mtd(name_localizations),
            description=description,
            description_localizations=mtd(description_localizations),
            options=[o._to_dict() for o in options]
            if options is not _MISSING
            else _MISSING,
            default_member_permissions=(
                default_member_permissions.value
                if isinstance(default_member_permissions, Permissions)
                else default_member_permissions
            ),
            integration_types=(
                [i.value for i in integration_types]
                if integration_types is not _MISSING
                else _MISSING
            ),
            contexts=(
                [c.value for c in contexts] if contexts is not _MISSING else _MISSING
            ),
            nsfw=nsfw,
        )

        return self._cache_storage.update_command(
            ApplicationCommand(
                await self._command_request(
                    method="PATCH",
                    command_id=command_id,
                    guild_id=guild_id,
                    json=payload,
                )
            )
        )

    async def delete(self, command_id: int, *, guild_id: int | None = None) -> None:
        """
        Deletes an application command.

        Parameters
        ----------
        command_id : :class:`int`
            The ID of the command to delete.

        guild_id : :class:`int`, optional
            The Guild ID of the Guild, if deleting a command scoped by guild.

        Raises
        ------
        :class:`NotFound`
            The command you tried to edit does not exist.

        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        await self._command_request(
            method="DELETE", command_id=command_id, guild_id=guild_id
        )
        self._cache_storage.remove_command(
            command_id=command_id, guild_id=guild_id or 0
        )
