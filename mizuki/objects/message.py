from __future__ import annotations
from datetime import datetime
from typing import Self

from ..enums.interaction import ApplicationIntegrationType
from ..enums.interaction import InteractionType
from ..enums.message import (
    BaseThemeType,
    MessageActivityType,
    MessageReferenceType,
    MessageType,
)
from ..flags import AttachmentFlags, MessageFlags
from ..payloads.message import (
    AttachmentPayload,
    AllowedMentionsPayload,
    MessageActivityPayload,
    MessageInteractionMetadataPayload,
    MessagePayload,
    MessageReferencePayload,
    MessageSnapshotPayload,
    PartialMessagePayload,
    PollAnswerCountPayload,
    PollAnswerPayload,
    PollMediaPayload,
    PollPayload,
    PollResultPayload,
    RoleSubscriptionDataPayload,
    SharedClientThemePayload,
)
from .._utils import scls, siso
from .channel import ChannelMention, ThreadChannel
from .embed import Embed
from .emoji import PartialEmoji, Reaction
from .snowflake import Snowflake
from .sticker import PartialSticker
from .user import User

__all__ = (
    "Attachment",
    "MessageReference",
    "MessageActivity",
    "PartialMessage",
    "MessageSnapshot",
    "MessageInteractionMetadata",
    "RoleSubscriptionData",
    "PollMedia",
    "PollAnswer",
    "PollAnswerCount",
    "PollResult",
    "Poll",
    "SharedClientTheme",
    "AllowedMentions",
    "Message",
)

class Attachment:
    __slots__ = (
        "id",
        "filename",
        "title",
        "description",
        "content_type",
        "size",
        "url",
        "proxy_url",
        "height",
        "width",
        "placeholder",
        "placeholder_version",
        "ephemeral",
        "duration_secs",
        "waveform",
        "flags",
        "clip_participants",
        "clip_created_at",
        "application",
    )

    def __init__(self, data: AttachmentPayload):
        self.id = Snowflake(data["id"])
        self.filename = data["filename"]
        self.title = data.get("title")
        self.description = data.get("description")
        self.content_type = data.get("content_type")
        self.size = data["size"]
        self.url = data["url"]
        self.proxy_url = data["proxy_url"]
        self.height = data.get("height")
        self.width = data.get("width")
        self.placeholder = data.get("placeholder")
        self.placeholder_version = data.get("placeholder_version")
        self.ephemeral = data.get("ephemeral", False)
        self.duration_secs = data.get("duration_secs")
        self.waveform = data.get("waveform")
        self.flags = AttachmentFlags(data.get("flags", 0))
        self.clip_participants = [User(u) for u in data.get("clip_participants", [])]
        self.clip_created_at = siso(data.get("clip_created_at"))
        self.application = data.get("application") # placeholder

class MessageReference:
    __slots__ = (
        "type",
        "message_id",
        "channel_id",
        "guild_id",
        "fail_if_not_exists"
    )

    def __init__(self, data: MessageReferencePayload):
        self.type = MessageReferenceType(data.get("type", 0))
        self.message_id = Snowflake._from_str(data.get("message_id"))
        self.channel_id = Snowflake._from_str(data.get("channel_id"))
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.fail_if_not_exists = data.get("fail_if_not_exists", True)

class MessageActivity:
    __slots__ = (
        "type",
        "party_id"
    )

    def __init__(self, data: MessageActivityPayload):
        self.type = MessageActivityType(data["type"])
        self.party_id = data.get("party_id")

class PartialMessage:
    __slots__ = (
        "content",
        "embeds",
        "attachments",
        "timestamp",
        "edited_timestamp",
        "flags",
        "mentions",
        "mention_roles",
        "type"
    )

    def __init__(self, data: PartialMessagePayload):
        self.content = data["content"]
        self.embeds = [Embed(e) for e in data["embeds"]]
        self.attachments = [Attachment(a) for a in data["attachments"]]
        self.timestamp = datetime.fromisoformat(data["timestamp"])
        self.edited_timestamp = siso(data["edited_timestamp"])
        self.flags = MessageFlags(data.get("flags", 0))
        self.mentions = [User(u) for u in data["mentions"]]
        self.mention_roles = [Snowflake(s) for s in data["mention_roles"]]
        self.type = MessageType(data["type"])

class MessageSnapshot:
    __slots__ = (
        "message",
    )

    def __init__(self, data: MessageSnapshotPayload):
        self.message = PartialMessage(data["message"])

class MessageInteractionMetadata:
    __slots__ = (
        "id",
        "type",
        "user",
        "authorizing_integration_owners",
        "original_response_message_id",
        "target_user",
        "target_message_id"
    )

    def __init__(self, data: MessageInteractionMetadataPayload):
        self.id = Snowflake(data["id"])
        self.type = InteractionType(data["type"])
        self.user = User(data["user"])
        self.authorizing_integration_owners = {ApplicationIntegrationType(int(a)): Snowflake(s) for a, s in data["authorizing_integration_owners"].items()}
        self.original_response_message_id = Snowflake._from_str(data.get("original_response_message_id"))
        self.target_user = scls(User, data.get("target_user"))
        self.target_message_id = Snowflake._from_str(data.get("target_message_id"))

class RoleSubscriptionData:
    __slots__ = (
        "role_subscription_listing_id",
        "tier_name",
        "total_months_subscribed",
        "is_renewal"
    )

    def __init__(self, data: RoleSubscriptionDataPayload):
        self.role_subscription_listing_id = Snowflake(data["role_subscription_listing_id"])
        self.tier_name = data["tier_name"]
        self.total_months_subscribed = data["total_months_subscribed"]
        self.is_renewal = data["is_renewal"]

class PollMedia:
    __slots__ = (
        "text",
        "emoji"
    )

    def __init__(self, data: PollMediaPayload):
        self.text = data["text"]
        self.emoji = scls(PartialEmoji, data.get("emoji"))

class PollAnswer:
    __slots__ = (
        "answer_id",
        "poll_media"
    )

    def __init__(self, data: PollAnswerPayload):
        self.answer_id = data["answer_id"]
        self.poll_media = PollMedia(data["poll_media"])

class PollAnswerCount:
    __slots__ = (
        "id",
        "count",
        "me_voted"
    )

    def __init__(self, data: PollAnswerCountPayload):
        self.id = data["id"]
        self.count = data["count"]
        self.me_voted = data["me_voted"]

class PollResult:
    __slots__ = (
        "is_finalized",
        "answer_counts"
    )

    def __init__(self, data: PollResultPayload):
        self.is_finalized = data["is_finalized"]
        self.answer_counts = [PollAnswerCount(p) for p in data["answer_counts"]]

class Poll:
    __slots__ = (
        "question",
        "answers",
        "expiry",
        "allow_multiselect",
        "layout_type",
        "results"
    )

    def __init__(self, data: PollPayload):
        self.question = PollMedia(data["question"])
        self.answers = [PollAnswer(p) for p in data["answers"]]
        self.expiry = siso(data["expiry"])
        self.allow_multiselect= data["allow_multiselect"]
        self.layout_type = data["layout_type"]
        self.results = scls(PollResult, data.get("results"))

class SharedClientTheme:
    __slots__ = (
        "colors",
        "gradient_angle",
        "base_mix",
        "base_theme"
    )

    def __init__(self, data: SharedClientThemePayload):
        self.colors = data["colors"]
        self.gradient_angle = data["gradient_angle"]
        self.base_mix = data["base_mix"]
        self.base_theme = scls(BaseThemeType, data.get("base_theme"))

class AllowedMentions:
    __slots__ = ("parse",)

    def __init__(self, data: AllowedMentionsPayload):
        self.parse = data["parse"]

    def _to_dict(self) -> AllowedMentionsPayload:
        return AllowedMentionsPayload(parse=self.parse)

    @classmethod
    def new(
        cls, *,
        roles: bool = True,
        users: bool = True,
        everyone: bool = True
    ) -> Self:
        parse = []
        if roles: parse.append("roles")
        if users: parse.append("users")
        if everyone: parse.append("everyone")
        return cls(AllowedMentionsPayload(parse=parse))

class Message(PartialMessage):
    __slots__ = (
        "id",
        "channel_id",
        "author",
        "tts",
        "mention_everyone",
        "mention_channels",
        "reactions",
        "nonce",
        "pinned",
        "webhook_id",
        "activity",
        "application",
        "application_id",
        "message_reference",
        "message_snapshots",
        "referenced_message",
        "interaction_metadata",
        "thread",
        "components",
        "sticker_items",
        "position",
        "role_subscription_data",
        "poll",
        "shared_client_theme"
    )
    
    def __init__(self, data: MessagePayload):
        super().__init__(data)
        self.id = Snowflake(data["id"])
        self.channel_id = Snowflake(data["channel_id"])
        self.author = User(data["author"])
        self.tts = data["tts"]
        self.mention_everyone = data["mention_everyone"]
        self.mention_channels = [ChannelMention(c) for c in data.get("mention_channels", [])]
        self.reactions = [Reaction(r) for r in data.get("reactions", [])]
        self.nonce = data.get("nonce")
        self.pinned = data["pinned"]
        self.webhook_id = Snowflake._from_str(data.get("webhook_id"))
        self.activity = scls(MessageActivity, data.get("activity"))
        self.application = data.get("application") # placehodler
        self.application_id = Snowflake._from_str(data.get("application_id"))
        self.message_reference = scls(MessageReference, data.get("message_reference"))
        self.message_snapshots = [MessageSnapshot(m) for m in data.get("message_snapshots", [])]
        self.referenced_message = scls(Message, data.get("referenced_message"))
        self.interaction_metadata = scls(MessageInteractionMetadata, data.get("interaction_metadata"))
        self.thread = scls(ThreadChannel, data.get("thread"))
        self.components = data.get("components", []) # placeholder
        self.sticker_items = [PartialSticker(s) for s in data.get("sticker_items", [])]
        self.position = data.get("position")
        self.role_subscription_data = scls(RoleSubscriptionData, data.get("role_subscription_data"))
        self.poll = scls(Poll, data.get("poll"))
        self.shared_client_theme = scls(SharedClientTheme, data.get("shared_client_theme"))