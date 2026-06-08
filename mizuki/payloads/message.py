from __future__ import annotations
from typing import Required, TypedDict, NotRequired, Literal
from ._types import ISO8601Timestamp, Snowflake, UNIMPLEMENTED
from .user import UserPayload
from .channel import ChannelMentionPayload, ThreadPayload
from .emoji import PartialEmojiPayload
from .embed import EmbedPayload
from .sticker import PartialStickerPayload

class AttachmentPayload(TypedDict, total=False):
    id: Required[Snowflake]
    filename: Required[str]
    title: str
    description: str
    content_type: str
    size: Required[int]
    url: Required[str]
    proxy_url: Required[str]
    height: str | None
    width: str | None
    placeholder: str
    placeholder_version: int
    ephemeral: bool
    duration_secs: float
    waveform: str
    flags: int
    clip_participants: list[UserPayload]
    clip_created_at: ISO8601Timestamp
    application: UNIMPLEMENTED

class ReactionCountDetailPayload(TypedDict):
    burst: int
    normal: int

class ReactionPayload(TypedDict):
    count: int
    count_detail: ReactionCountDetailPayload
    me: bool
    me_burst: bool
    emoji: PartialEmojiPayload
    burst_colors: list[int]
    
class MessageReferencePayload(TypedDict, total=False):
    type: Literal[0, 1]
    message_id: Snowflake
    channel_id: Snowflake
    guild_id: Snowflake
    fail_if_not_exists: bool
    
class PartialMessagePayload(TypedDict):
    content: str | None
    embeds: list[EmbedPayload]
    attachments: list[AttachmentPayload]
    timestamp: ISO8601Timestamp
    edited_timestamp: ISO8601Timestamp | None
    flags: NotRequired[int]
    mentions: list[UserPayload]
    mention_roles: list[Snowflake]
    type: Required[Literal[
        0, 1, 2, 6, 7, 8, 9,
        10, 11, 12, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 31,
        32, 36, 37, 38, 39, 44, 46,
    ]]
    
class MessageSnapshotPayload(TypedDict):
    message: PartialMessagePayload
        
class MessageInteractionMetadataPayload(TypedDict):
    id: Snowflake
    type: Literal[1, 2, 3, 4, 5]
    user: UserPayload
    authorizing_integration_owners: dict[Literal[0, 1], Snowflake]
    original_response_message_id: NotRequired[Snowflake]
    target_user: NotRequired[UserPayload]
    target_message_id: NotRequired[Snowflake]

class RoleSubscriptionDataPayload(TypedDict):
    role_subscription_listing_id: Snowflake
    tier_name: str
    total_months_subscribed: int
    is_renewal: bool

class PollMediaPayload(TypedDict):
    text: str
    emoji: NotRequired[PartialEmojiPayload]
    
class PollAnswerPayload(TypedDict):
    answer_id: int
    poll_media: PollMediaPayload
    
class PollAnswerCountPayload(TypedDict):
    id: int
    count: int
    me_voted: bool
    
class PollResultPayload(TypedDict):
    is_finalized: bool
    answer_counts: list[PollAnswerCountPayload]
    
class PollPayload(TypedDict):
    question: PollMediaPayload
    answers: list[PollAnswerPayload]
    expiry: ISO8601Timestamp | None
    allow_multiselect: bool
    layout_type: Literal[1]
    results: NotRequired[PollResultPayload]
    
class SharedClientThemePayload(TypedDict):
    colors: list[str]
    gradient_angle: int
    base_mix: int
    base_theme: NotRequired[Literal[0, 1, 2, 3, 4] | None]
    
class MessageActivityPayload(TypedDict):
    type: Literal[1, 2, 3, 5]
    party_id: NotRequired[str]

class AllowedMentionsPayload(TypedDict):
    parse: list[Literal["roles", "users", "everyone"]]
        
class MessagePayload(PartialMessagePayload, total=False):
    id: Required[Snowflake]
    channel_id: Required[Snowflake]
    author: Required[UserPayload]
    tts: Required[bool]
    mention_everyone: Required[bool]
    mention_channels: list[ChannelMentionPayload]
    reactions: list[ReactionPayload]
    nonce: str | int
    pinned: Required[bool]
    webhook_id: Snowflake
    activity: MessageActivityPayload
    application: UNIMPLEMENTED
    application_id: Snowflake
    message_reference: MessageReferencePayload
    message_snapshots: list[MessageSnapshotPayload]
    referenced_message: MessagePayload | None
    interaction_metadata: MessageInteractionMetadataPayload
    thread: ThreadPayload
    components: list[UNIMPLEMENTED]
    sticker_items: list[PartialStickerPayload]
    position: int
    role_subscription_data: RoleSubscriptionDataPayload
    # resolved object currently Skipped
    poll: PollPayload
    # call skipped as never accessible
    shared_client_theme: SharedClientThemePayload
