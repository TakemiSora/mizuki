from datetime import datetime

from ..enums.user import PremiumType
from ..flags import UserFlags
from ..payloads.user import PartialUserPayload, UserPayload
from .._utils import scls
from .asset import Asset
from .avatar_decoration import AvatarDecoration
from .collectibles import Nameplate
from .primary_guild import UserPrimaryGuild
from .snowflake import Snowflake

__all__ = (
    "PartialUser",
    "User",
)

class PartialUser:
    __slots__ = (
        "id",
    )

    def __init__(self, data: PartialUserPayload):
        self.id = Snowflake(data["id"])

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id
            
    @property
    def created_at(self) -> datetime:
        return self.id.created_at

class User(PartialUser):
    __slots__ = (
        "name",
        "discriminator",
        "global_name",
        "avatar",
        "bot",
        "system",
        "mfa_enabled",
        "banner",
        "accent_color",
        "locale",
        "verified",
        "email",
        "flags",
        "_premium_type",
        "avatar_decoration",
        "nameplate",
        "primary_guild",
        "member"
    )
    def __init__(self, data: UserPayload):
        super().__init__(data)
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
        self.flags = UserFlags(data.get("flags", 0))
        self._premium_type = data.get("premium_type")
        self.avatar_decoration = scls(AvatarDecoration, data.get("avatar_decoration_data"))
        nameplate_data = (data.get("collectibles") or {}).get("nameplate")
        self.nameplate = scls(Nameplate, nameplate_data)
        self.primary_guild = scls(UserPrimaryGuild, data.get("primary_guild"))

    def __str__(self) -> str:
        return self.name
    
    @property
    def premium(self) -> PremiumType | None:
        """
        Returns `PremiumType.NONE` if the user has no Nitro or you are missing `identify.premium` scope.
        """
        if self._premium_type is None:
            return None
        return PremiumType(self._premium_type)
