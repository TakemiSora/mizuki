from typing import Any
from .asset import Asset
from .flags import RoleFlags

class RoleColors:
    def __init__(self, data: dict[str, int | None]):
        self.primary: int = data["primary_color"]
        self.secondary = data.get("secondary_color")
        self.tertiary = data.get("tertiary_color")

class Role:
    def __init__(self, data: dict[str, Any]):            
        self.id = int(data["id"])
        self.name: str = data["name"]
        self.colors = RoleColors(data["colors"])
        self.hoist: bool = data["hoist"]
        self.icon = Asset._from_role_icon(self.id, data.get("icon"))
        self.emoj: str | None = data.get("unicode_emoji")
        self.position: int = data["position"]
        #implement permissions later
        self.managed: bool = data["managed"]
        self.mentionable: bool = data["mentionable"]
        #implement roletags later
        self.flags = RoleFlags(data["flags"])

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id