from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from mizuki._utils import _MISSING, mgetattr, scls
from mizuki.enums.user import PremiumType
from mizuki.flags import MessageFlags, UserFlags
from mizuki.objects.asset import Asset
from mizuki.objects.avatar_decoration import AvatarDecoration
from mizuki.objects.collectibles import Nameplate
from mizuki.objects.primary_guild import UserPrimaryGuild
from mizuki.objects.snowflake import Snowflake
from mizuki.payloads.user import PartialUserPayload, UserPayload

if TYPE_CHECKING:
    from mizuki.file import File
    from mizuki.objects.channel import PrivateChannel
    from mizuki.objects.components import Component
    from mizuki.objects.embed import Embed
    from mizuki.objects.message import AllowedMentions, Message, MessageReference
    from mizuki.state import ConnectionState

__all__ = (
    "PartialUser",
    "User",
)


class PartialUser:
    """Represents a partial user object."""

    __slots__ = (
        "_channel",
        "_state",
        "id",
    )

    id: Snowflake
    "The ID of the user."

    def __init__(self, data: PartialUserPayload, *, state: ConnectionState):
        self._channel = None
        self._state = state
        self.id = Snowflake(data["id"])

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented

    def __hash__(self) -> int:
        return self.id

    @property
    def created_at(self) -> datetime:
        """Returns the date the account was created at."""
        return self.id.created_at

    async def fetch_full(self) -> User:
        """Fetches a :class:`User <mizuki.objects.user.User>` from the Discord API.

        Raises
        ------
        :class:`NotFound`
            Could not find an user with that ID.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.users.fetch(self.id)

    async def create_dm_channel(self) -> PrivateChannel:
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
        self._channel = await self._state.managers.users.create_dm_channel(self.id)
        return self._channel

    async def send(
        self,
        *,
        content: str = _MISSING,
        tts: bool = _MISSING,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        message_reference: MessageReference = _MISSING,
        files: list[File] = _MISSING,
        sticker_ids: list[int] = _MISSING,
        flags: MessageFlags = _MISSING,
    ) -> Message:
        """Sends a message to this user.

        .. note::

            At least one of, ``content``, ``embeds``, ``sticker_ids``, ``files`` must be provided. For forwarding, only ``message_reference`` must be provided.

        Parameters
        ----------
        content : :class:`str`
            The content of the message.

        tts : :class:`bool`
            Whether TTS is enabled for the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`]
            The list of embeds to send along the message.

        components : list[:class:`Component <mizuki.objects.component.Component>`]
            The list of components to send in this message.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled.

        files : list[:class:`File <mizuki.file.File>`]
            The files to upload with the message.

        message_reference : :class:`MessageReference <mizuki.objects.message.MessageReference>`
            The reference message for the new message, if any

        sticker_ids : list[:class:`int`]
            The Guild Stickers to send with the message. Max 3.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`
            The MessageFlags of the new message.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to send to doesn't exist.

        :class:`Forbidden`
            You are not allowed to send the message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.create(
            (
                mgetattr(self._channel, "id", cast_to=int | None)
                or (await self.create_dm_channel()).id
            ),
            content=content,
            tts=tts,
            embeds=embeds,
            components=components,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            files=files,
            sticker_ids=sticker_ids,
            flags=flags,
        )


class User(PartialUser):
    """Represents a user in Discord."""

    __slots__ = (
        "_premium_type",
        "accent_color",
        "avatar",
        "avatar_decoration",
        "banner",
        "bot",
        "discriminator",
        "flags",
        "global_name",
        "locale",
        "member",
        "mfa_enabled",
        "nameplate",
        "primary_guild",
        "system",
        "username",
    )

    username: str
    "The username of the user."

    discriminator: str
    "The discriminator of the user."

    global_name: str | None
    "The user's display name if it is set."

    avatar: Asset | None
    "The avatar of the user."

    bot: bool
    "Whether the user is a bot."

    system: bool
    "Whether this user is an Official Discord System user."

    mfa_enabled: bool
    "Whether the user has 2fa enabled on their account."

    banner: Asset | None
    "The banner of the user."

    accent_color: int | None
    "The user's banner color encoded in a hexadecimal color code."

    locale: str | None
    "The chosen language option of the user."

    flags: UserFlags
    "The flags of the user."

    avatar_decoration: AvatarDecoration | None
    "The avatar decoration the user is using."

    nameplate: Nameplate | None
    "The nameplate of the user."

    primary_guild: UserPrimaryGuild | None
    "The primary guild of the user (the guild that they're using the guild tag of)."

    def __init__(self, data: UserPayload, *, state: ConnectionState):
        super().__init__(data, state=state)
        self.username = data["username"]
        self.discriminator = data["discriminator"]
        self.global_name = data["global_name"]
        self.avatar = Asset._from_user_avatar(self.id, data["avatar"])
        self.bot = data.get("bot", False)
        self.system = data.get("system", False)
        self.mfa_enabled = data.get("mfa_enabled", False)
        self.banner = Asset._from_user_banner(self.id, data.get("banner"))
        self.accent_color = data.get("accent_color")
        self.locale = data.get("locale")
        self.flags = UserFlags(data.get("flags", 0))
        self._premium_type = data.get("premium_type")
        self.avatar_decoration = scls(
            AvatarDecoration, data.get("avatar_decoration_data")
        )
        nameplate_data = (data.get("collectibles") or {}).get("nameplate")
        self.nameplate = scls(Nameplate, nameplate_data)
        self.primary_guild = scls(UserPrimaryGuild, data.get("primary_guild"))

    def __str__(self) -> str:
        return self.username

    @property
    def premium(self) -> PremiumType | None:
        """Returns `PremiumType.NONE` if the user has no Nitro or you are missing `identify.premium` scope."""
        if self._premium_type is None:
            return None
        return PremiumType(self._premium_type)
