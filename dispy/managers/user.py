from ._types import BaseManager
from ..http import Path
from ..objects.user import User

__all__ = (
    "UserManager",
)

class UserManager(BaseManager):
    """
    Manager used to fetch :class:`User <dispy.objects.user.User>` objects.
    """

    __slots__ = ()
    
    async def fetch_me(self) -> User:
        """
        Fetches the user object of the bot. This should generally not be called as it is accessible on startup via :attr:`Bot.user <dispy.bot.Bot.user>`.
        
        Raises
        ------
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_users(
            User(
                await self._http.request(
                    Path(
                        "GET",
                        "users/@me"
            )))
        )

    def get(self, user_id: int) -> User | None:
        """
        Attempts to fetch a :class:`User <dispy.objects.user.User>` from the internal cache of the bot.
        
        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.
            
        Returns
        -------
        :class:`User <dispy.objects.user.User>`
            The User received from the cache.
        :class:`None`
            Could not find the User object in the internal cache.
        """
        return self._cache_storage.get_user(user_id)

    async def fetch(self, user_id: int) -> User:
        """
        Attempts to fetch a :class:`User <dispy.objects.user.User>` from the Discord API.
        
        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.
            
        Returns
        -------
        :class:`User <dispy.objects.user.User>`
            The User object recieved from Discord API.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an user with that ID.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_users(
            User(await self._http.request(
                Path(
                    "GET",
                    "users/{user_id}",
                    user_id=user_id
            )))
        )

    async def get_or_fetch(self, user_id: int) -> User:
        """
        A couroutine function that attempts to fetch a :class:`User <dispy.objects.user.User>` from internal cache and if not present, makes an API call to discord.
        
        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.
            
        Returns
        -------
        :class:`User <dispy.objects.user.User>`
            The User object recieved from Discord API or cache.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an user with that ID.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(user_id) or await self.fetch(user_id)