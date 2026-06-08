from enum import IntEnum, StrEnum

__all__ = (
    "GuildVerificationLevel",
    "GuildNotificationLevel",
    "GuildExplicitContentLevel",
    "GuildMFALevel",
    "GuildPremiumTier",
    "GuildNSFWLevel",
    "GuildFeature",
    "GuildScheduledEventStatus",
    "GuildScheduledEventEntityType",
    "EventRecurrenceRuleFrequency",
    "EventRecurrenceRuleMonth",
    "EventRecurrenceRuleWeekday"
)
    
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

class GuildScheduledEventStatus(IntEnum):
    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELED = 4
    
class GuildScheduledEventEntityType(IntEnum):
    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3
    
class EventRecurrenceRuleFrequency(IntEnum):
    YEARLY = 0
    MONTHLY = 1
    WEEKLY = 2
    DAILY = 3
    
class EventRecurrenceRuleWeekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY =  6
    
class EventRecurrenceRuleMonth(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12