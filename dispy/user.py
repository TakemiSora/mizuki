from typing import Any
from .asset import Asset
from .flags import UserFlags
from .enums import NitroType
from .state import State
from .collectibles import Nameplate
from .primary_guild import UserPrimaryGuild
from .avatar_decoration import AvatarDecoration

class User:
    def __init__(self, state: State, data: dict[str, Any]):
        self._state = state

        self.id: int = int(data["id"])
        self.name: str = data["username"]
        self.discriminator: str | None = data.get("discriminator")
        self.global_name: str | None = data.get("global_name")
        self.avatar = Asset._from_user_avatar(state, self.id, data.get("avatar"))
        self.bot: bool = data.get("bot", False)
        self.system: bool = data.get("system", False)
        self.mfa_enabled: bool = data.get("mfa_enabled", False)
        self.banner = Asset._from_user_banner(state, self.id, data.get("banner"))
        self.accent_color: int | None = data.get("accent_color")
        self.locale: str | None = data.get("locale")
        self.verified: bool = data.get("verified", False)
        self.email: str | None = data.get("email")
        self.flags = UserFlags._from_int(data.get("flags"))
        self.public_flags = UserFlags._from_int(data.get("public_flags"))
        self._nitro_type: int | None = data.get("premium_type")
        self.avatar_decoration = AvatarDecoration._from_dict(state, data.get("avatar_decoration_data"))
        nameplate_data = (data.get("collectibles") or {}).get("nameplate")
        self.nameplate = Nameplate._from_dict(state, nameplate_data)
        self.primary_guild = UserPrimaryGuild._from_dict(state, data.get("primary_guild"))

    def __str__(self) -> str:
        return self.name

    @property
    def nitro(self) -> NitroType | None:
        if self._nitro_type is None:
            return None
        return NitroType(self._nitro_type)
