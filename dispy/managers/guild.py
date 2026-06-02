from ._types import BaseManager
from ..http import Path
from ..objects.guild import Guild

__all__ = (
    "GuildManager",
)

class GuildManager(BaseManager):
    """
    Manager used to fetch :class:`Guild <dispy.objects.guild.Guild>` objects.
    """

    __slots__ = ()

    def get(self, guild_id: int) -> Guild | None:
        """
        Attempts to fetch a :class:`Guild <dispy.objects.guild.Guild>` from the internal cache of the bot.
        
        Parameters
        ----------
        guild_id: :class:`int`
            The guild_id of the guild to fetch.
            
        Returns
        -------
        :class:`Guild <dispy.objects.guild.Guild>`
            The Guild received from the cache.
        :class:`None`
            Could not find the Guild object in the internal cache.
        """
        return self._cache_storage.get_guild(guild_id)

    async def fetch(self, guild_id: int) -> Guild:
        """
        Attempts to fetch a :class:`Guild <dispy.objects.guild.Guild>` from the Discord API.
        
        Parameters
        ----------
        guild_id: :class:`int`
            The guild_id of the guild to fetch.
            
        Returns
        -------
        :class:`Guild <dispy.objects.guild.Guild>`
            The Message object recieved from Discord API.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an guild with that ID.
        :class:`Forbidden`
            You are not allowed to fetch that guild.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_guilds(
            Guild(await self._http.request(
                Path(
                    "GET",
                    "guilds/{guild_id}",
                    guild_id=guild_id
            )))
        )
    
    async def get_or_fetch(self, guild_id: int) -> Guild:
        """
        A couroutine function that attempts to fetch a :class:`Guild <dispy.objects.guild.Guild>` from internal cache and if not present, makes an API call to discord.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild_id of the guild to fetch.
            
        Returns
        -------
        :class:`Guild <dispy.objects.guild.Guild>`
            The Message object recieved from Discord API.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an guild with that ID.
        :class:`Forbidden`
            You are not allowed to fetch that guild.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(guild_id) or await self.fetch(guild_id)