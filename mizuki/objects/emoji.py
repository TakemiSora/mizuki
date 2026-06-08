from .user import User
from .asset import Asset
from .snowflake import Snowflake
from datetime import datetime
from ..payloads.emoji import PartialEmojiPayload, EmojiPayload, ActivityEmojiPayload
from ..payloads.channel import DefaultReactionPayload
from ..payloads.message import ReactionCountDetailPayload, ReactionPayload
from .._utils import scls

__all__ = (
    "ActivityEmoji",
    "PartialEmoji",
    "Emoji",
    "DefaultReaction",
    "Reaction",
    "ReactionCountDetail"
)

class ActivityEmoji:
    __slots__ = (
        "id",
        "name",
        "animated"
    )
    
    def __init__(self, data: ActivityEmojiPayload):
        self.id = Snowflake._from_str(data.get("id"))
        self.name = data["name"]
        self.animated = data.get("animated", False)

class PartialEmoji:
    __slots__ = (
        "id",
        "animated",
        "name",
        "asset"
    )
    
    def __init__(self, data: PartialEmojiPayload):
        self.id = Snowflake._from_str(data["id"])
        self.animated = data.get("animated", False)
        self.name = data["name"]
        self.asset  = Asset._from_custom_emoji(self.id, self.animated) if self.id else None
        
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
        "asset"
    )
    
    def __init__(self, data: EmojiPayload):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.roles = data["roles"] # maybe later when cache and everything is working ill do full zrole Obkects
        self.user = scls(User, data.get("user"))
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
    __slots__ = (
        "emoji_id",
        "emoji_name"
    )

    def __init__(self, data: DefaultReactionPayload):
        self.emoji_id = Snowflake._from_str(data["emoji_id"])
        self.emoji_name = data["emoji_name"]

class ReactionCountDetail:
    __slots__ = (
        "burst",
        "normal"
    )

    def __init__(self, data: ReactionCountDetailPayload):
        self.burst = data["burst"]
        self.normal = data["normal"]

class Reaction:
    __slots__ = (
        "count",
        "count_detail",
        "me",
        "me_burst",
        "emoji",
        "burst_colors"
    )
    
    def __init__(self, data: ReactionPayload):
        self.count = data["count"]
        self.count_detail = ReactionCountDetail(data["count_detail"])
        self.me = data["me"]
        self.me_burst = data["me_burst"]
        self.emoji = PartialEmoji(data["emoji"])
        self.burst_colors = data["burst_colors"]