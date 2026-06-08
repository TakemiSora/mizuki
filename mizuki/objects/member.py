from datetime import datetime, timezone
from typing import overload, Self

from ..flags import GuildMemberFlags
from ..payloads.member import MemberPayload, PartialMemberPayload
from .._utils import scls, sint, siso
from .asset import Asset
from .avatar_decoration import AvatarDecoration
from .collectibles import Nameplate
from .permissions import Permissions
from .snowflake import Snowflake
from .user import User

__all__ = (
    "PartialMember",
    "Member",
)

class PartialMember:
    __slots__ = (
        "guild_id",
        "id",
        "nick",
        "asset",
        "banner",
        "roles",
        "joined_at",
        "premium_since",
        "flags",
        "pending",
        "permissions",
        "communication_disabled_until",
        "avatar_decoration_data",
        "nameplate"
    )
    
    def __init__(self, data: PartialMemberPayload, *, guild_id: int, user_id: int):
        self.guild_id = Snowflake(guild_id)
        self.id = Snowflake(user_id)
        self.nick = data.get("nick")
        self.asset = Asset._from_member_avatar(guild_id, user_id, data.get("avatar"))
        self.banner = Asset._from_member_banner(guild_id, user_id, data.get("banner"))
        self.roles = [int(r) for r in data["roles"]]
        self.joined_at = siso(data["joined_at"])
        self.premium_since = siso(data["premium_since"])
        self.flags = GuildMemberFlags(data["flags"])
        self.pending = data.get("pending", False)
        self.permissions = Permissions(sint(data.get("permissions", "0")))
        self.communication_disabled_until = siso(data.get("communication_disabled_until"))
        self.avatar_decoration_data = scls(AvatarDecoration, data.get("avatar_decoration_data"))
        collectibles = data.get("collectibles")
        nameplate = collectibles.get("nameplate") if collectibles else None
        self.nameplate = scls(Nameplate, nameplate)
        
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

class ResolvedMember(PartialMember):
    __slots__ = ("user",)

    @classmethod
    def _from_partial_member(cls, member: PartialMember, *, user: User) -> Self:
        self = cls.__new__(cls)
        for slot in PartialMember.__slots__:
            setattr(self, slot, getattr(member, slot))
        self.user = user
        return self

class Member(PartialMember):
    __slots__ = (
        "user",
        "deaf",
        "mute",
    )

    @overload
    def __init__(self, data: MemberPayload, *, guild_id: int, user_id: None = None) -> None: ...

    @overload
    def __init__(self, data: MemberPayload, *, guild_id: int, user_id: int) -> None: ...

    def __init__(self, data: MemberPayload, *, guild_id: int, user_id: int | None = None):
        self.user = scls(User, data.get("user"))
        user_id = int(self.user.id) if self.user is not None else user_id
        if user_id is None:
            raise ValueError("Both user object and user_id cannot be None for a member object.")
        super().__init__(data, guild_id=guild_id, user_id=user_id)

        self.deaf = data["deaf"]
        self.mute = data["mute"]