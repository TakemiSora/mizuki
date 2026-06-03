from ._types import BaseManager
from ..http import HTTPClient, Path
from ..cache import CacheStorage
from ..objects.command import ApplicationCommand, PartialApplicationCommand

class CommandManager(BaseManager):
    """
    Manager used to manage :class:`ApplicationCommands <dispy.objects.command.ApplicationCommand>`.
    """

    __slots__ = (
        "_application_id",
    )
    
    def __init__(self, client: HTTPClient, storage: CacheStorage, application_id: int):
        super().__init__(client, storage)
        self._application_id = application_id
        
    async def fetch_all(self, *, with_localizations: bool = True) -> list[ApplicationCommand]:
        """
        Fetches a list of all global application commands from the Discord API.
        
        .. note::

            This method should generally not be called as the library will cache the commands on startup. Prefer to use :meth:`get_all() <dispy.managers.command.CommandManager.get_all>` for fetching a list of your application commands.
        
        Returns
        -------
        list[:class:`ApplicationCommand <dispy.objects.command.ApplicationCommand>`]

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.replace_all_commands(
            [
                ApplicationCommand(c)
                for c in await self._http.request(
                    Path(
                        "GET",
                        "applications/{application_id}/commands?with_localizations={with_localizations}",
                        application_id=self._application_id,
                        with_localizations=with_localizations
            ))]
        )

    def get_all(self) -> list[ApplicationCommand]:
        """
        Returns a list of Application commands from internal cache.

        Returns
        -------
        list[:class:`ApplicationCommand <dispy.objects.command.ApplicationCommand>`]
        """
        return self._cache_storage.get_all_commands()

    async def sync(self, command: PartialApplicationCommand) -> ApplicationCommand:
        """
        Syncs a specific command object to the Discord API.

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.add_command(
            ApplicationCommand(
                await self._http.request(
                    Path(
                        "POST",
                        "applications/{application_id}/commands",
                        application_id=self._application_id
                    ),
                    json=command._to_dict()
                )
            )
        )

    async def sync_bulk(self, commands: list[PartialApplicationCommand]) -> list[ApplicationCommand]:
        """
        Syncs given commands to the Discord API. This will override all commands currently synced.

        Raises
        ------
        :class:`Unauthorized`
            You are not authorized. Your token may be invalid.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.add_commands_bulk([
            ApplicationCommand(c)
            for c in
            await self._http.request(
                Path(
                    "PUT",
                    "applications/{application_id}/commands",
                    application_id=self._application_id
                ),
                json=[c._to_dict() for c in commands]
            )
        ])