from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, cast

from mizuki._utils import scls, siso
from mizuki.enums.invite import InviteTargetType, InviteType
from mizuki.flags import InviteFlags
from mizuki.objects.channel import PartialGuildChannel
from mizuki.objects.guild import Guild, GuildScheduledEvent
from mizuki.objects.role import PartialRole
from mizuki.objects.user import User
from mizuki.payloads.invite import InviteMetadataPayload, InvitePayload

if TYPE_CHECKING:
    from mizuki.state import ConnectionState

__all__ = ("Invite", "InviteMetadata")


class Invite:
    __slots__ = (
        "_state",
        "approximate_member_count",
        "approximate_presence_count",
        "channel",
        "code",
        "expires_at",
        "flags",
        "guild",
        "guild_scheduled_event",
        "inviter",
        "roles",
        "target_type",
        "target_user",
        "type",
    )

    def __init__(self, data: InvitePayload, *, state: ConnectionState):
        self._state = state
        self.type = InviteType(data["type"])
        self.code = data["code"]
        self.guild = scls(Guild, data.get("guild"), state=self._state)
        self.channel = scls(
            PartialGuildChannel,
            data["channel"],
            guild_id=self.guild.id if self.guild is not None else None,
        )
        self.inviter = scls(User, data.get("inviter"), state=state)
        self.target_type = scls(InviteTargetType, data.get("target_type"))
        self.target_user = scls(User, data.get("target_user"), state=state)
        self.approximate_presence_count = data.get("approximate_presence_count")
        self.approximate_member_count = data.get("approximate_member_count")
        self.expires_at = siso(data["expires_at"])
        self.guild_scheduled_event = scls(
            GuildScheduledEvent, data.get("guild_scheduled_event"), state=state
        )
        self.flags = scls(InviteFlags, data.get("flags"))
        self.roles = [
            PartialRole(p, guild_id=cast(Guild, self.guild).id, state=state)
            for p in data.get("roles", [])
        ]


class InviteMetadata(Invite):
    __slots__ = ("created_at", "max_age", "max_uses", "temporary", "uses")

    def __init__(self, data: InviteMetadataPayload, *, state: ConnectionState):
        super().__init__(data, state=state)
        self.uses = data["uses"]
        self.max_uses = data["max_uses"]
        self.max_age = data["max_age"]
        self.temporary = data["temporary"]
        self.created_at = datetime.fromisoformat(data["created_at"])
