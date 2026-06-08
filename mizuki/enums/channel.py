from enum import IntEnum

__all__ = (
    "ChannelType",
    "ChannelPermissionOverwriteType",
    "VideoQualityMode",
    "SortOrderType",
    "ForumLayoutType"
)

class ChannelType(IntEnum):
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