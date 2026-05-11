from typing import Any
from .asset import Asset
from .enums import (
    GuildVerificationLevel,
    GuildNotificationLevel,
    GuildExplicitContentLevel,
    GuildFeature, GuildMFALevel,
    GuildPremiumTier, GuildNSFWLevel
)
from .sticker import Sticker
from .role import Role
from .emoji import Emoji
from .utils import sint
from .snowflake import Snowflake
from datetime import datetime

class Guild:    
    def __init__(self, data: dict[str, Any]):
        self.id = Snowflake(data["id"])
        self.name: str = data["name"]
        self.icon = Asset._from_guild_avatar(self.id, data.get("icon"))
        self.splash = Asset._from_guild_splash(self.id, data.get("splash"))
        self.discovery_splash = Asset._from_guild_discovery_splash(self.id, data.get("discovery_splash"))
        self.owner_id = Snowflake(data["owner_id"])
        self.afk_channel_id = Snowflake._from_str(data["afk_channel_id"])
        self.afk_timeout: int = data["afk_timeout"]
        self.verification_level = GuildVerificationLevel(data["verification_level"])
        self.notification_level = GuildNotificationLevel(data["default_message_notifications"])
        self.explicit_level = GuildExplicitContentLevel(data["explicit_content_filter"])
        self.roles = [Role(r) for r in data["roles"]]
        self.emojis = [Emoji(e) for e in data["emojis"]]
        self.features: set[GuildFeature] = set(GuildFeature(f) for f in data["features"])
        self.mfa_level = GuildMFALevel(data["mfa_level"])
        self.application_id = Snowflake._from_str(data["application_id"])
        self.system_channel_id = Snowflake._from_str(data["system_channel_id"])
        self.max_presences = sint(data.get("max_presences"))
        self.max_members = sint(data.get("max_members"))
        self.vanity_url_code: str | None = data["vanity_url_code"]
        self.description: str | None = data.get("description")
        self.banner = Asset._from_guild_banner(self.id, data["banner"])
        self.premium_tier = GuildPremiumTier(data["premium_tier"])
        self.premium_subscription_count: int = data.get("premium_subscription_count", 0)
        self.preferred_locale: str = data["preferred_locale"]
        self.public_updates_channel_id = Snowflake._from_str(data["public_updates_channel_id"])
        self.max_video_channel_users: int | None = data.get("max_video_channel_users")
        self.max_stage_video_channel_users: int | None = data.get("max_stage_video_channel_users")
        self.approximate_member_count: int | None = data.get("approximate_member_count")
        self.approximate_presence_count: int | None = data.get("approximate_presence_count")
        self.nsfw_level = GuildNSFWLevel(data["nsfw_level"])
        self.stickers = [Sticker(s) for s in data.get("stickers", [])]
        self.premium_progress_bar_enabled: bool = data["premium_progress_bar_enabled"]        
        self.safety_alerts_channel_id = Snowflake._from_str(data["safety_alerts_channel_id"])
        
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id
            
    @property
    def created_at(self) -> datetime:
        return self.id.created_at