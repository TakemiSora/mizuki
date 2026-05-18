from enum import IntFlag
from typing import Self

__all__ = (
    "UserFlags",
    "RoleFlags",
    "IntentFlags",
    "SystemChannelFlags",
    "GuildMemberFlags",
    "ChannelFlags"
)

class UserFlags(IntFlag):
    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSEUDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_BOT_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19

class RoleFlags(IntFlag):
    IN_PROMPT = 1 << 0
    
class IntentFlags(IntFlag):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EXPRESSIONS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATUS = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21
    GUILD_MESSAGE_POLLS = 1 << 24
    DIRECT_MESSAGE_POLLS = 1 << 25

    @classmethod
    def all(cls) -> Self:
        val = 0
        for f in cls:
            val |= f

        return cls(val)

    @classmethod
    def standard(cls) -> Self:
        priviledged = cls.GUILD_PRESENCES | cls.MESSAGE_CONTENT | cls.GUILD_MEMBERS
        return cls.all() & ~priviledged

class SystemChannelFlags(IntFlag):
    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 1 << 2
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 1 << 3
    SUPPRESS_ROLE_SUBSCRIPTION_PURCHASE_NOTIFICATIONS = 1 << 4

class GuildMemberFlags(IntFlag):
    DID_REJOIN = 1 << 0
    COMPLETED_ONBOARDING = 1 << 1
    BYPASSES_VERIFICATION = 1 << 2
    STARTED_ONBOARDING = 1 << 3
    IS_GUEST = 1 << 4
    STARTED_HOME_ACTIONS = 1 << 5
    COMPLETED_HOME_ACTIONS = 1 << 6
    AUTOMOD_QUARANTINED_USERNAME = 1 << 7
    DM_SETTINGS_UPSELL_ACKNOWLEDGED = 1 << 8
    AUTOMOD_QUARANTINED_GUILD_TAG = 1 << 9

class ChannelFlags(IntFlag):
    PINNED = 1 << 1
    REQUIRE_TAG = 1 << 4
    HIDE_MEDIA_DOWNLOAD_OPTIONS = 1 << 15