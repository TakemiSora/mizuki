from datetime import datetime

from ..enums.presence import ActivityType, PresenceStatusType, StatusDisplayType
from ..flags import ActivityFlags
from ..payloads.presence import (
    ActivityAssetsPayload,
    ActivityButtonPayload,
    ActivityPartyPayload,
    ActivityPayload,
    ActivitySecretsPayload,
    PresencePayload,
    TimestampsPayload,
)
from .._utils import scls
from .asset import activity_asset_parse
from .emoji import ActivityEmoji
from .snowflake import Snowflake
from .user import User

__all__ = (
    "Activity",
    "Presence"
)

class ActivityTimestamps:
    __slots__ = (
        "start",
        "end"
    )

    def __init__(self, data: TimestampsPayload):
        self.start = scls(datetime.fromtimestamp, data.get("start"))
        self.end = scls(datetime.fromtimestamp, data.get("end"))
        
class ActivityParty:
    __slots__ = (
        "id",
        "size"
    )
    
    def __init__(self, data: ActivityPartyPayload):
        self.id = data.get("id")
        self.size = data.get("size")
        
    @property
    def current_size(self) -> int | None:
        return self.size[0] if self.size is not None else None
            
    @property
    def max_size(self) -> int | None:
        return self.size[1] if self.size is not None else None
            
class ActivityAssets:
    __slots__ = (
        "large_image",
        "large_text",
        "large_url",
        "small_image",
        "small_text",
        "small_url",
        "invite_cover_image"
    )
    
    def __init__(self, data: ActivityAssetsPayload, *, application_id: int | None):
        self.large_image = activity_asset_parse(application_id, data.get("large_image"))
        self.large_text = data.get("large_text")
        self.large_url = data.get("large_url")
        self.small_image = activity_asset_parse(application_id, data.get("small_image"))
        self.small_text = data.get("small_text")
        self.small_url = data.get("small_url")
        self.invite_cover_image = activity_asset_parse(application_id, data.get("invite_cover_image"))
        
class ActivitySecrets:
    __slots__ = (
        "join",
        "spectate",
        "match"
    )
    
    def __init__(self, data: ActivitySecretsPayload):
        self.join = data.get("join")
        self.spectate = data.get("spectate")
        self.match = data.get("match")
        
class ActivityButton:
    __slots__ = (
        "label",
        "url"
    )
    
    def __init__(self, data: ActivityButtonPayload):
        self.label = data["label"]
        self.url = data["url"]

class Activity:
    __slots__ = (
        "name",
        "type",
        "url",
        "created_at",
        "timestamps",
        "application_id",
        "status_display_type",
        "details",
        "details_url",
        "state",
        "state_url",
        "emoji",
        "party",
        "assets",
        "secrets",
        "instance",
        "flags",
        "buttons",
    )

    def __init__(self, data: ActivityPayload):
        self.name = data["name"]
        self.type = ActivityType(data["type"])
        self.url = data.get("url")
        self.created_at = datetime.fromtimestamp(data["created_at"])
        self.timestamps = scls(ActivityTimestamps, data.get("timestamps"))
        self.application_id = Snowflake._from_str(data.get("application_id"))
        self.status_display_type = scls(StatusDisplayType, data.get("status_display_type"))
        self.details = data.get("details")
        self.details_url = data.get("details_url")
        self.state = data.get("state")
        self.state_url = data.get("state_url")
        self.emoji = scls(ActivityEmoji, data.get("emoji"))
        self.party = scls(ActivityParty, data.get("party"))
        self.assets = scls(ActivityAssets, data.get("assets"))
        self.secrets = scls(ActivitySecrets, data.get("secrets"))
        self.instance = data.get("instance", False)
        self.flags = scls(ActivityFlags, data.get("flags"))
        self.buttons = [ActivityButton(a) for a in data.get("buttons", [])]

class Presence:
    __slots__ = (
        "user",
        "guild_id",
        "status",
        "activities"
    )
    
    def __init__(self, data: PresencePayload):
        self.user = User(data["user"])
        self.guild_id = Snowflake(data["guild_id"])
        self.status = PresenceStatusType(data["status"])
        self.activities = [Activity(a) for a in data["activities"]]