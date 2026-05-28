from __future__ import annotations
from typing import Literal, Required, TypedDict
from ._types import UNIMPLEMENTED, Permissions, Snowflake
from .channel import (
    GuildChannelPayload,
    ThreadPayload,
    PartialGuildChannelPayload,
    PartialThreadPayload,
    PrivateChannelPayload,
)
from .embed import EmbedPayload
from .guild import GuildPayload
from .member import MemberPayload, PartialMemberPayload
from .message import AttachmentPayload, MessagePayload, PartialMessagePayload
from .role import RolePayload
from .user import UserPayload

class ResolvedDataPayload(TypedDict, total=False):
    users: dict[Snowflake, UserPayload]
    members: dict[Snowflake, PartialMemberPayload]
    roles: dict[Snowflake, RolePayload]
    channels: dict[Snowflake, PartialGuildChannelPayload | PartialThreadPayload]
    messages: dict[Snowflake, PartialMessagePayload]
    attachments: dict[Snowflake, AttachmentPayload]

class ApplicationCommandInteractionOptionPayload(TypedDict, total=False):
    name: Required[str]
    type: Required[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
    value: str | int | float | bool
    options: list[ApplicationCommandInteractionOptionPayload]
    focused: bool

class InvokedApplicationCommandPayload(TypedDict, total=False):
    id: Required[Snowflake]
    name: Required[str]
    type: Required[Literal[1, 2, 3, 4]]
    resolved: ResolvedDataPayload
    options: list[ApplicationCommandInteractionOptionPayload]
    guild_id: Snowflake
    target_id: Snowflake

InteractionData = InvokedApplicationCommandPayload
AuthorizingIntegrationOwnersDict = dict[Literal[0, 1], Snowflake | Literal[0]]

class InteractionPayload(TypedDict, total=False):
    id: Required[Snowflake]
    application_id: Required[Snowflake]
    type: Required[Literal[1, 2, 3, 4, 5]]
    data: InteractionData
    guild: GuildPayload
    guild_id: Snowflake
    channel: GuildChannelPayload | ThreadPayload | PrivateChannelPayload
    channel_id: Snowflake
    member: MemberPayload
    user: UserPayload
    token: Required[str]
    version: Required[Literal[1]]
    message: MessagePayload
    app_permissions: Required[Permissions]
    locale: str
    guild_locale: str
    # skippinf entitlements as of now
    authorizing_integration_owners: Required[AuthorizingIntegrationOwnersDict]
    context: Literal[0, 1, 2]
    attachment_size_limit: Required[int]
        
class InteractionCallbackDataPayload(TypedDict, total=False):
    tts: bool
    content: str
    embeds: list[EmbedPayload]
    allowed_mentions: Literal["roles", "users", "everyone"]
    flags: int
    components: list[UNIMPLEMENTED]
    attachments: list[UNIMPLEMENTED]
    poll: UNIMPLEMENTED
    
class InteractionResponseCallbackPayload(TypedDict, total=False):
    type: Literal[1, 4, 5, 6, 7, 8, 9, 10, 12]
    data: InteractionCallbackDataPayload