from datetime import datetime
from ..payloads.channel import *
from .snowflake import Snowflake
from ..enums.channel import ChannelType, VideoQualityMode, SortOrderType, ForumLayoutType
from ..flags import ChannelFlags
from .permissions import Permissions, ChannelPermissionOverwrite
from ..utils import siso, scls
from .member import Member
from .user import User

__all__ = (
    "ThreadMetaData",
    "ThreadMember",
    "ForumTag",
    "GuildChannel",
    "ThreadChannel",
    "PrivateChannel"
)

class ThreadMetaData:
    __slots__ = (
        "archived",
        "auto_archive_duration",
        "archive_timestamp",
        "locked",
        "invitable",
        "create_timestamp"
    )
    
    def __init__(self, data: ThreadMetaDataPayload):
        self.archived = data["archived"]
        self.auto_archive_duration = data["auto_archive_duration"]
        self.archive_timestamp = datetime.fromisoformat(data["archive_timestamp"])
        self.locked = data["locked"]
        self.invitable = data.get("invitable", False)
        self.create_timestamp = siso(data.get("create_timestamp"))
        
class ThreadMember:
    __slots__ = (
        "id",
        "user_id",
        "join_timestamp",
        "flags",
        "member"
    )
    
    def __init__(self, data: ThreadMemberPayload, guild_id: int | None = None, user_id: int | None = None):
        self.id = data.get("id")
        self.user_id = data.get("user_id")
        self.join_timestamp = datetime.fromisoformat(data["join_timestamp"])
        self.flags = data["flags"]
        if guild_id and user_id:
            self.member = scls(Member, data.get("member"), guild_id=guild_id, user_id=user_id)
        else:
            self.member = None

class ForumTag:
    __slots__ = (
        "id",
        "name",
        "moderated",
        "emoji_id",
        "emoji_name"
    )

    def __init__(self, data: ForumTagPayload):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.moderated = data["moderated"]
        self.emoji_id = Snowflake._from_str(data.get("emoji_id"))
        self.emoji_name = data["emoji_name"]

class BaseChannel:
    __slots__ = (
        "id",
        "last_message_id",
        "flags",
        "last_pin_timestamp"
    )

    def __init__(self, data: BaseChannelPayload):
        self.id = Snowflake(data["id"])
        self.last_message_id = Snowflake._from_str(data.get("last_message_id"))
        self.flags = ChannelFlags(data["flags"])
        self.last_pin_timestamp = siso(data.get("last_pin_timestamp"))

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id
    
    @property
    def created_at(self) -> datetime:
        return self.id.created_at

class BasePublicChannel(BaseChannel):
    __slots__ = (
        "guild_id",
        "name",
        "parent_id",
        "rate_limit_per_user",
        "bitrate",
        "user_limit",
        "rtc_region",
        "video_quality_mode",
        "permissions",
    )

    def __init__(self, data: BasePublicChannelPayload):
        super().__init__(data)
        self.guild_id = Snowflake(data["guild_id"])
        self.name = data["name"]
        self.parent_id = Snowflake._from_str(data.get("parent_id"))
        self.rate_limit_per_user = data.get("rate_limit_per_user")
        self.bitrate = data.get("bitrate")
        self.user_limit = data.get("user_limit")
        self.rtc_region = data.get("rtc_region")
        self.video_quality_mode = scls(VideoQualityMode, data.get("video_quality_mode"))
        self.permissions = scls(Permissions, data.get("permissions"))

class GuildChannel(BasePublicChannel):
    __slots__ = (
        "type",
        "topic",
        "default_auto_archive_duration",
        "default_thread_rate_limit_per_user",
        "position",
        "permission_overwrites",
        "nsfw",
        "available_tags",
        "default_sort_order",
        "default_forum_layout",
    )

    def __init__(self, data: GuildChannelPayload):
        super().__init__(data)
        self.type = ChannelType(data["type"])
        self.topic = data.get("topic")
        self.default_auto_archive_duration = data.get("default_auto_archive_duration")
        self.default_thread_rate_limit_per_user = data.get("default_thread_rate_limit_per_user")
        self.position = data["position"]
        self.permission_overwrites = [ChannelPermissionOverwrite(p) for p in data.get("permission_overwrites", [])]
        self.nsfw = data.get("nsfw", False)
        self.available_tags = [ForumTag(f) for f in data.get("available_tags", [])]
        self.default_sort_order = scls(SortOrderType, data.get("default_sort_order"))
        self.default_forum_layout = scls(ForumLayoutType, data.get("default_forum_layout"))
        
class ThreadChannel(BasePublicChannel):
    __slots__ = (
        "type",
        "owner_id",
        "thread_metadata",
        "message_count",
        "member_count",
        "total_message_sent",
        "applied_tags",
        "member"
    )
    
    def __init__(self, data: ThreadPayload):
        super().__init__(data)
        self.type = ChannelType(data["type"])
        self.owner_id = Snowflake(data["owner_id"])
        self.thread_metadata = ThreadMetaData(data["thread_metadata"])
        self.message_count = data["message_count"]
        self.member_count = data["member_count"]
        self.total_message_sent = data["total_message_sent"]
        self.applied_tags = [Snowflake(s) for s in data["applied_tags"]]
        self.member = ThreadMember(data["member"])
        
class PrivateChannel(BaseChannel):
    __slots__ = (
        "recipients",
        "type"
    )
    
    def __init__(self, data: PrivateChannelPayload):
        super().__init__(data)
        self.recipients = [User(u) for u in data["recipients"]]
        self.type = ChannelType(data["type"])