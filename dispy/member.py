from datetime import datetime, timezone
from .payloads.member import MemberPayload
from .user import User
from .asset import Asset
from .flags import GuildMemberFlags
from .permissions import Permissions
from .utils import siso, sint
from .avatar_decoration import AvatarDecoration
from .collectibles import Nameplate
from .snowflake import Snowflake
from typing import Self

__all__ = (
    "Member",
)

class Member:
    __slots__ = (
        "user",
        "guild_id",
        "id",
        "nick",
        "asset",
        "banner",
        "roles",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "flags",
        "pending",
        "permissions",
        "communication_disabled_until",
        "avatar_decoration_data",
        "nameplate"
    )

    def __init__(self, data: MemberPayload, *, guild_id: int, user_id: int):
        user = data.get("user")
        if user:
            self.user = User(user)
        else:
            self.user = None

        self.guild_id = Snowflake(guild_id)
        self.id = Snowflake(user_id)

        self.nick = data.get("nick")
        self.asset = Asset._from_member_avatar(guild_id, user_id, data.get("avatar"))
        self.banner = Asset._from_member_banner(guild_id, user_id, data.get("banner"))
        self.roles = [int(r) for r in data["roles"]]
        self.joined_at = siso(data["joined_at"])
        self.premium_since = siso(data["premium_since"])
        self.deaf = data["deaf"]
        self.mute = data["mute"]
        self.flags = GuildMemberFlags(data["flags"])
        self.pending = data.get("pending", False)
        self.permissions = Permissions(sint(data.get("permissions", "0")))
        self.communication_disabled_until = siso(data.get("communication_disabled_until"))
        self.avatar_decoration_data = AvatarDecoration._from_dict(data.get("avatar_decoration_data"))
        collectibles = data.get("collectibles")
        nameplate = collectibles.get("nameplate") if collectibles else None
        self.nameplate = Nameplate._from_dict(nameplate)
        
    @classmethod
    def _from_dict(cls, data: MemberPayload | None, *, guild_id: int, user_id: int) -> Self | None:
        if data is not None:
            return cls(data, guild_id=guild_id, user_id=user_id)
        return None

    @property
    def is_timed_out(self) -> bool:
        return datetime.now(timezone.utc) > self.communication_disabled_until if self.communication_disabled_until else False

    @property
    def created_at(self) -> datetime:
        return self.id.created_at

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented