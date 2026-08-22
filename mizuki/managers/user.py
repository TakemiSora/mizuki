from mizuki._utils import _MISSING, assign_val_dict
from mizuki.file import File
from mizuki.http import Path
from mizuki.managers._types import BaseManager
from mizuki.objects.channel import PrivateChannel
from mizuki.objects.guild import Guild
from mizuki.objects.member import Member
from mizuki.objects.user import User

__all__ = ("UserManager",)


class UserManager(BaseManager):
    """Manager used to fetch :class:`User <mizuki.objects.user.User>` objects."""

    __slots__ = ()

    async def fetch_me(self) -> User:
        """Fetches the user object of the bot. This should generally not be called as it is accessible on startup via :attr:`Bot.user <mizuki.bot.Bot.user>`.

        Raises
        ------
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_users(
            User(
                await self._state.http.request(Path("GET", "users/@me")),
                state=self._state,
            )
        )

    def get(self, user_id: int) -> User | None:
        """Attempts to fetch a :class:`User <mizuki.objects.user.User>` from the internal cache of the bot.

        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.
        """
        return self._cache_storage.get_user(user_id)

    async def fetch(self, user_id: int) -> User:
        """Attempts to fetch a :class:`User <mizuki.objects.user.User>` from the Discord API.

        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.

        Raises
        ------
        :class:`NotFound`
            Could not find an user with that ID.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_users(
            User(
                await self._state.http.request(
                    Path("GET", "users/{user_id}", user_id=user_id)
                ),
                state=self._state,
            )
        )

    async def get_or_fetch(self, user_id: int) -> User:
        """A couroutine function that attempts to fetch a :class:`User <mizuki.objects.user.User>` from internal cache and if not present, makes an API call to discord.

        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.

        Returns
        -------
        :class:`User <mizuki.objects.user.User>`
            The User object recieved from Discord API or cache.

        Raises
        ------
        :class:`NotFound`
            Could not find an user with that ID.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(user_id) or await self.fetch(user_id)

    async def edit_me(
        self,
        username: str = _MISSING,
        avatar: File | str | None = _MISSING,
        banner: File | str | None = _MISSING,
    ) -> User:
        """Edits the bot's profile.

        Parameters
        ----------
        username : :class:`str`, optional
            The username of the bot.

        avatar : :class:`File <mizuki.file.File>` | :class:`str` | :class:`None`, optional
            The avatar for the bot.

        banner : :class:`File <mizuki.file.File>` | :class:`str` | :class:`None`, optional
            The banner for the bot.

        Raises
        ------
        :class:`HTTPException`
            An HTTP error occured.``
        """

        if isinstance(avatar, str):
            avatar = File(avatar)
        if isinstance(banner, str):
            banner = File(banner)

        return self._cache_storage.update_users(
            User(
                await self._state.http.request(
                    Path("PATCH", "users/@me"),
                    json=assign_val_dict(
                        {},
                        _MISSING,
                        username=username,
                        avatar=(
                            await avatar.encode_to_image_data_uri()
                            if not (avatar is _MISSING or avatar is None)
                            else avatar
                        ),
                        banner=(
                            await banner.encode_to_image_data_uri()
                            if not (banner is _MISSING or banner is None)
                            else banner
                        ),
                    ),
                ),
                state=self._state,
            )
        )

    async def fetch_self_guilds(
        self,
        after: int = _MISSING,
        before: int = _MISSING,
        limit: int = _MISSING,
        with_counts: bool = True,
    ) -> list[Guild]:
        """Fetches the guild of the current bot user.

        Parameters
        ----------
        after : :class:`int`, optional
            To fetch the guilds after this ID.

        before : :class:`int`, optional
            To fetch the guilds before this ID.

        limit : :class:`int`, optional
            The amount of guilds to fetch. Can be from 1-200.

        with_counts : :class:`bool`, optional
            Whether to fetch the guilds with their counts.

        Raises
        ------
        :class:`HTTPException`
            An HTTP error occured.
        """
        return [
            self._cache_storage.update_guilds(Guild(g, state=self._state))
            for g in await self._state.http.request(
                Path("GET", "users/@me/guilds"),
                params=assign_val_dict(
                    {},
                    _MISSING,
                    before=before,
                    after=after,
                    limit=limit,
                    with_counts=str(with_counts),
                ),
            )
        ]

    async def fetch_guild_member(self, guild_id: int) -> Member:
        """Fetches the member object for the bot in a guild.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the guild to fetch the member in.

        Raises
        ------
        :class:`Forbidden`
            You are not allowed to fetch that resource.

        :class:`NotFound`
            Could not find an guild with that ID.

        :class:`HTTPException`
            An HTTP error occured.
        """
        return Member(
            await self._state.http.request(
                Path("GET", "users/@me/guilds/{guild_id}/member", guild_id=guild_id)
            ),
            guild_id=guild_id,
            state=self._state,
        )

    async def leave_guild(self, guild_id: int) -> None:
        """Leave a guild from the bot.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the guild to leave.

        Raises
        ------
        :class:`NotFound`
            Could not find an guild with that ID that you are in.

        :class:`HTTPException`
            An HTTP error occured.
        """
        await self._state.http.request(
            Path("DELETE", "users/@me/guilds/{guild_id}", guild_id=guild_id)
        )

    async def create_dm_channel(self, recipient_id: int) -> PrivateChannel:
        """Creates a private channel with a user and/or returns the channel.

        Parameters
        ----------
        recipient_id : :class:`int`
            The ID of the user to create the DM channel with.

        Raises
        ------
        :class:`NotFound`
            The user you tried to create the channel with does not exist.

        :class:`HTTPException`
            An HTTP error occured.
        """
        return self._cache_storage.update_channels(
            PrivateChannel(
                await self._state.http.request(
                    Path("POST", "users/@me/channels"),
                    json={"recipient_id": recipient_id},
                ),
                state=self._state,
            )
        )
