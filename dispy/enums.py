from enum import IntEnum as BaseIntEnum, StrEnum as BaseStrEnum
from typing import Self

__all__ = (
    "PremiumType",
    "StickerType",
    "StickerFormatType",
    "GuildVerificationLevel",
    "GuildNotificationLevel",
    "GuildExplicitContentLevel",
    "GuildMFALevel",
    "GuildPremiumTier",
    "GuildNSFWLevel",
    "GuildFeature",
    "ChannelType",
    "ChannelPermissionOverwriteType",
    "VideoQualityMode",
    "SortOrderType",
    "ForumLayoutType"
)

class IntEnum(BaseIntEnum):
    @classmethod
    def _from_val(cls, val: int | None) -> Self | None:
        if val is not None:
            return cls(val)
        return None
        
class StrEnum(BaseStrEnum):
    @classmethod
    def _from_val(cls, val: str | None) -> Self | None:
        if val is not None:
            return cls(val)
        return None

class PremiumType(IntEnum):
    NONE = 0
    CLASSIC = 1
    NITRO = 2
    BASIC = 3
    
class StickerType(IntEnum):
    STICKER = 1
    GUILD = 2
    
class StickerFormatType(IntEnum):
    PNG = 1
    APNG = 2
    LOTTIE = 3
    GIF = 4
    
    def __str__(self) -> str:
        return {
            1: "png",
            2: "png",
            3: "lottie",
            4: "gif"
        }[self.value]

class GuildVerificationLevel(IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4
    
class GuildNotificationLevel(IntEnum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1
    
class GuildExplicitContentLevel(IntEnum):
    DISABLED = 0
    MEMBER_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2

class GuildMFALevel(IntEnum):
    NONE = 0
    ELEVATED = 1
    
class GuildPremiumTier(IntEnum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3
    
class GuildNSFWLevel(IntEnum):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3
        
class GuildFeature(StrEnum):
    ANIMATED_BANNER = "ANIMATED_BANNER"
    ANIMATED_ICON = "ANIMATED_ICON"
    APPLICATION_COMMAND_PERMISSIONS_V2 = "APPLICATION_COMMAND_PERMISSIONS_V2"
    AUTO_MODERATION = "AUTO_MODERATION"
    BANNER = "BANNER"
    COMMUNITY = "COMMUNITY"
    CREATOR_MONETIZABLE_PROVISIONAL = "CREATOR_MONETIZABLE_PROVISIONAL"
    CREATOR_STORE_PAGE = "CREATOR_STORE_PAGE"
    DEVELOPER_SUPPORT_SERVER = "DEVELOPER_SUPPORT_SERVER"
    DISCOVERABLE = "DISCOVERABLE"
    FEATURABLE = "FEATURABLE"
    INVITES_DISABLED = "INVITES_DISABLED"
    INVITE_SPLASH = "INVITE_SPLASH"
    MEMBER_VERIFICATION_GATE_ENABLED = "MEMBER_VERIFICATION_GATE_ENABLED"
    MORE_SOUNDBOARD = "MORE_SOUNDBOARD"
    MORE_STICKERS = "MORE_STICKERS"
    NEWS = "NEWS"
    PARTNERED = "PARTNERED"
    PREVIEW_ENABLED = "PREVIEW_ENABLED"
    RAID_ALERTS_DISABLED = "RAID_ALERTS_DISABLED"
    ROLE_ICONS = "ROLE_ICONS"
    ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE = "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE"
    ROLE_SUBSCRIPTIONS_ENABLED = "ROLE_SUBSCRIPTIONS_ENABLED"
    SOUNDBOARD = "SOUNDBOARD"
    TICKETED_EVENTS_ENABLED = "TICKETED_EVENTS_ENABLED"
    VANITY_URL = "VANITY_URL"
    VERIFIED = "VERIFIED"
    VIP_REGIONS = "VIP_REGIONS"
    WELCOME_SCREEN_ENABLED = "WELCOME_SCREEN_ENABLED"
    GUESTS_ENABLED = "GUESTS_ENABLED"
    GUILD_TAGS = "GUILD_TAGS"
    ENHANCED_ROLE_COLORS = "ENHANCED_ROLE_COLORS"

class ChannelType(IntEnum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 1
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15
    GUILD_MEDIA = 16

class ChannelPermissionOverwriteType(IntEnum):
    ROLE = 0
    MEMBER = 1

class VideoQualityMode(IntEnum):
    AUTO = 1
    FULL = 2

class SortOrderType(IntEnum):
    LATEST_ACTIVITY = 0
    CREATION_DATE = 1

class ForumLayoutType(IntEnum):
    NOT_SET = 0
    LIST_VIEW = 1
    GALLERY_VIEW = 2