from enum import IntEnum

__all__ = (
    "ChannelPermissionOverwriteType",
    "ChannelType",
    "ForumLayoutType",
    "SortOrderType",
    "VideoQualityMode",
)


class ChannelType(IntEnum):
    """Represents the type of a channel."""

    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
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
    """Represents a type (role/member) for a permission overwrite of a channel."""

    ROLE = 0
    MEMBER = 1


class VideoQualityMode(IntEnum):
    """Represents the video quality in a voice channel."""

    AUTO = 1
    FULL = 2


class SortOrderType(IntEnum):
    """The sort order for a guild forum/media channel."""

    LATEST_ACTIVITY = 0
    CREATION_DATE = 1


class ForumLayoutType(IntEnum):
    """The layout for a guild media channel."""

    NOT_SET = 0
    LIST_VIEW = 1
    GALLERY_VIEW = 2
