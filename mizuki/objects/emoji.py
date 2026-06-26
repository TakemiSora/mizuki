from __future__ import annotations
from datetime import datetime
from typing import Self, TYPE_CHECKING

from mizuki._utils import _MISSING, assign_val, scls
from mizuki.objects.asset import Asset
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.user import User
from mizuki.payloads.channel import DefaultReactionPayload
from mizuki.payloads.emoji import (
    ActivityEmojiPayload,
    EmojiPayload,
    PartialEmojiPayload,
)
from mizuki.payloads.message import ReactionCountDetailPayload, ReactionPayload

if TYPE_CHECKING:
    from mizuki.state import ConnectionState

__all__ = (
    "ActivityEmoji",
    "PartialEmoji",
    "Emoji",
    "DefaultReaction",
    "Reaction",
    "ReactionCountDetail",
)


class ActivityEmoji:
    __slots__ = ("id", "name", "animated")

    def __init__(self, data: ActivityEmojiPayload):
        self.id = Snowflake._from_str(data.get("id"))
        self.name = data["name"]
        self.animated = data.get("animated", False)


class PartialEmoji:
    __slots__ = ("id", "animated", "name", "asset")

    def __init__(self, data: PartialEmojiPayload):
        self.id = Snowflake._from_str(data["id"])
        self.animated = data.get("animated", False)
        self.name = data["name"]
        self.asset = (
            Asset._from_custom_emoji(self.id, self.animated) if self.id else None
        )

    @property
    def created_at(self) -> datetime | None:
        return self.id.created_at if self.id else None

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, (PartialEmoji, Emoji)):
            if self.id is not None:
                return self.id == obj.id
            return self.name == obj.name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id or self.name)


class Emoji:
    __slots__ = (
        "id",
        "name",
        "roles",
        "user",
        "require_colons",
        "managed",
        "animated",
        "available",
        "asset",
    )

    def __init__(self, data: EmojiPayload, *, state: ConnectionState):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.roles = data[
            "roles"
        ]  # maybe later when cache and everything is working ill do full zrole Obkects
        self.user = scls(User, data.get("user"), state=state)
        self.require_colons = data.get("require_colons", False)
        self.managed = data.get("managed", False)
        self.animated = data.get("animated", False)
        self.available = data.get("available", False)
        self.asset = Asset._from_custom_emoji(self.id, self.animated)

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented

    def __hash__(self) -> int:
        return self.id


class DefaultReaction:
    """
    Represents a Default Reaction object that is shown in every thread in a :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA` channel.
    """

    __slots__ = ("emoji_id", "emoji_name")

    emoji_id: Snowflake | None
    "The ID of the emoji. It is None for a unicode emoji."

    emoji_name: str | None
    "The unicode emoji. It is None for a custom emoji."

    def __init__(self, data: DefaultReactionPayload):
        self.emoji_id = Snowflake._from_str(data["emoji_id"])
        self.emoji_name = data["emoji_name"]

    def _to_dict(self) -> DefaultReactionPayload:
        return DefaultReactionPayload(
            emoji_id=str(self.emoji_id), emoji_name=self.emoji_name
        )

    @classmethod
    def new(cls, *, emoji_id: int = _MISSING, emoji_name: str = _MISSING) -> Self:
        """
        Creates a new instance of a DefaultReaction Object.

        .. note::

            Exactly one of ``emoji_id`` and ``emoji_name`` must be passed.


        Parameters
        ----------
        emoji_id : :class:`int`, optional
            The ID of the custom emoji.

        emoji_name : :class:`str`, optional
            The unicode emoji.
        """
        return assign_val(cls.__new__(cls), emoji_id=emoji_id, emoji_name=emoji_name)


class ReactionCountDetail:
    __slots__ = ("burst", "normal")

    def __init__(self, data: ReactionCountDetailPayload):
        self.burst = data["burst"]
        self.normal = data["normal"]


class Reaction:
    __slots__ = ("count", "count_detail", "me", "me_burst", "emoji", "burst_colors")

    def __init__(self, data: ReactionPayload):
        self.count = data["count"]
        self.count_detail = ReactionCountDetail(data["count_detail"])
        self.me = data["me"]
        self.me_burst = data["me_burst"]
        self.emoji = PartialEmoji(data["emoji"])
        self.burst_colors = data["burst_colors"]
