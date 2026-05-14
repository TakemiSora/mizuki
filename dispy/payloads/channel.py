from typing import Literal, NotRequired, TypedDict
from .member import MemberPayload
from .user import UserPayload
from ._types import CDNHash, ISO8601Timestamp, Permissions, Snowflake

class ChannelPermissionOverwritePayload(TypedDict):
    id: Snowflake
    type: Literal[0, 1]
    allow: Permissions
    deny: Permissions

class ThreadMetaDataPayload(TypedDict):
    archived: bool
    auto_archive_duration: int
    archive_timestamp: ISO8601Timestamp
    locked: bool
    invitable: NotRequired[bool]
    create_timestamp: NotRequired[ISO8601Timestamp | None]

class ThreadMemberPayload(TypedDict):
    id: NotRequired[Snowflake]
    user_id: NotRequired[Snowflake]
    join_timestamp: ISO8601Timestamp
    flags: int
    member: NotRequired[MemberPayload]

class ForumTagPayload(TypedDict):
    id: Snowflake
    name: str
    moderated: bool
    emoji_id: Snowflake | None
    emoji_name: str | None

class DefaultReactionPayload(TypedDict):
    emoji_id: Snowflake | None
    emoji_name: str | None
    
class GuildChannelResponse(TypedDict):
    id: Snowflake
    type: Literal[0, 2, 4, 5, 13, 14, 15]
    last_message_id: NotRequired[Snowflake | None]
    flags: int
    last_pin_timestamp: NotRequired[ISO8601Timestamp | None]
    guild_id: Snowflake
    name: str
    parent_id: NotRequired[Snowflake | None]
    rate_limit_per_user: NotRequired[int]
    bitrate: NotRequired[int]
    user_limit: NotRequired[int]
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[int]
    permissions: NotRequired[str]
    topic: NotRequired[str | None]
    default_auto_archive_duration: NotRequired[int]
    default_thread_rate_limit_per_user: NotRequired[int]
    position: int
    permission_overwrites: NotRequired[list[ChannelPermissionOverwritePayload]]
    nsfw: NotRequired[bool]
    available_tags: NotRequired[list[ForumTagPayload]]
    default_reaction_emoji: NotRequired[DefaultReactionPayload | None]
    default_sort_order: NotRequired[int | None]
    default_forum_layout: NotRequired[int]

class PrivateChannelResponse(TypedDict):
    id: Snowflake
    type: Literal[1]
    last_message_id: NotRequired[Snowflake | None]
    flags: int
    last_pin_timestamp: NotRequired[ISO8601Timestamp | None]
    recipients: list[UserPayload]

class PrivateGroupChannelResponse(TypedDict):
    id: Snowflake
    type: Literal[3]
    last_message_id: NotRequired[Snowflake | None]
    flags: int
    last_pin_timestamp: NotRequired[ISO8601Timestamp | None]
    recipients: list[UserPayload]
    name: str | None
    icon: CDNHash | None
    owner_id: Snowflake
    managed: NotRequired[bool]
    application_id: NotRequired[Snowflake]

class ThreadResponse(TypedDict):
    id: Snowflake
    type: Literal[10, 11, 12]
    last_message_id: NotRequired[Snowflake | None]
    flags: int
    last_pin_timestamp: NotRequired[ISO8601Timestamp | None]
    guild_id: int
    name: str
    parent_id: NotRequired[Snowflake | None]
    rate_limit_per_user: NotRequired[int]
    bitrate: NotRequired[int]
    user_limit: NotRequired[int]
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[int]
    permissions: NotRequired[str]
    owner_id: Snowflake
    thread_metadata: ThreadMetaDataPayload
    message_count: int
    member_count: int
    total_message_sent: int
    applied_tags: list[Snowflake]
    member: ThreadMemberPayload