from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from mizuki.flags import InviteFlags
from mizuki._utils import scls, siso

from mizuki.payloads.invite import InviteMetadataPayload, InvitePayload
from mizuki.enums.invite import InviteType, InviteTargetType
from mizuki.objects.channel import PartialGuildChannel
from mizuki.objects.user import User
from mizuki.objects.role import PartialRole
from mizuki.objects.guild import Guild, GuildScheduledEvent

if TYPE_CHECKING:
    from mizuki.state import ConnectionState

__all__ = ("Invite", "InviteMetadata")


class Invite:
    __slots__ = (
        "_state",
        "type",
        "code",
        "guild",
        "channel",
        "inviter",
        "target_type",
        "target_user",
        "approximate_presence_count",
        "approximate_member_count",
        "expires_at",
        "guild_scheduled_event",
        "flags",
        "roles",
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
        self.roles = [PartialRole(p) for p in data.get("roles", [])]


class InviteMetadata(Invite):
    __slots__ = ("uses", "max_uses", "max_age", "temporary", "created_at")

    def __init__(self, data: InviteMetadataPayload, *, state: ConnectionState):
        super().__init__(data, state=state)
        self.uses = data["uses"]
        self.max_uses = data["max_uses"]
        self.max_age = data["max_age"]
        self.temporary = data["temporary"]
        self.created_at = datetime.fromisoformat(data["created_at"])
