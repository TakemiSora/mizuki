from typing import Literal, Required, TypedDict

from ._types import CDNHash, Snowflake, UnixTime
from .user import UserPayload
from .emoji import ActivityEmojiPayload

class TimestampsPayload(TypedDict, total=False):
    start: UnixTime
    end: UnixTime

class ActivityPartyPayload(TypedDict, total=False):
    id: str
    size: list[int]

ActivityImage = str | CDNHash

class ActivityAssetsPayload(TypedDict, total=False):
    large_image: ActivityImage
    large_text: str
    large_url: str
    small_image: ActivityImage
    small_text: str
    small_url: str
    invite_cover_image: ActivityImage

class ActivitySecretsPayload(TypedDict, total=False):
    join: str
    spectate: str
    match: str

class ActivityButtonPayload(TypedDict):
    label: str
    url: str

class ActivityPayload(TypedDict, total=False):
    name: Required[str]
    type: Required[Literal[0, 1, 2, 3, 4, 5]]
    url: str | None
    created_at: Required[UnixTime]
    timestamps: TimestampsPayload
    application_id: Snowflake
    status_display_type: Literal[0, 1, 2] | None
    details: str | None
    details_url: str | None
    state: str | None
    state_url: str | None
    emoji: ActivityEmojiPayload | None
    party: ActivityPartyPayload
    assets: ActivityAssetsPayload
    secrets: ActivitySecretsPayload
    instance: bool
    flags: int
    buttons: list[ActivityButtonPayload]

class PresencePayload(TypedDict):
    user: UserPayload
    guild_id: Snowflake
    status: Literal["idle", "dnd", "online", "offline"]
    activities: list[ActivityPayload]