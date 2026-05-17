from __future__ import annotations
from .asset import Asset
from ..flags import UserFlags
from ..enums.user import PremiumType
from .collectibles import Nameplate
from .primary_guild import UserPrimaryGuild
from .avatar_decoration import AvatarDecoration
from .snowflake import Snowflake
from datetime import datetime
from ..payloads.user import UserPayload

__all__ = (
    "User",
)

class User:
    def __init__(self, data: UserPayload):
        self.id = Snowflake(data["id"])
        self.name = data["username"]
        self.discriminator = data["discriminator"]
        self.global_name  = data["global_name"]
        self.avatar = Asset._from_user_avatar(self.id, data["avatar"])
        self.bot = data.get("bot", False)
        self.system = data.get("system", False)
        self.mfa_enabled = data.get("mfa_enabled", False)
        self.banner = Asset._from_user_banner(self.id, data.get("banner"))
        self.accent_color = data.get("accent_color")
        self.locale = data.get("locale")
        self.verified = data.get("verified", False)
        self.email= data.get("email")
        self.flags = UserFlags._from_int(data.get("flags"))
        self.public_flags = UserFlags._from_int(data.get("public_flags"))
        self._premium_type = data.get("premium_type")
        self.avatar_decoration = AvatarDecoration._from_dict(data.get("avatar_decoration_data"))
        nameplate_data = (data.get("collectibles") or {}).get("nameplate")
        self.nameplate = Nameplate._from_dict(nameplate_data)
        self.primary_guild = UserPrimaryGuild._from_dict(data.get("primary_guild"))

    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id
            
    @classmethod
    def _from_dict(cls, data: UserPayload | None) -> User | None:
        return cls(data) if data is not None else None
            
    @property
    def created_at(self) -> datetime:
        return self.id.created_at

    @property
    def premium(self) -> PremiumType | None:
        """
        Returns `PremiumType.NONE` if the user has no Nitro or you are missing `identify.premium` scope.
        """
        if self._premium_type is None:
            return None
        return PremiumType(self._premium_type)
