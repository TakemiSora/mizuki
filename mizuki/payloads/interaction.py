from __future__ import annotations
from typing import Literal, Required, TypedDict

from mizuki.payloads._types import UNIMPLEMENTED, Permissions, Snowflake
from mizuki.payloads.channel import (
    PartialGuildChannelPayload,
    PartialThreadPayload,
    PrivateChannelPayload,
)
from mizuki.payloads.components import ComponentResponsePayload
from mizuki.payloads.embed import EmbedPayload
from mizuki.payloads.file import FileUploadPayload
from mizuki.payloads.guild import GuildPayload
from mizuki.payloads.member import MemberPayload, PartialMemberPayload
from mizuki.payloads.message import (
    AttachmentPayload,
    MessagePayload,
    PartialMessagePayload,
    AllowedMentionsPayload,
)
from mizuki.payloads.role import RolePayload
from mizuki.payloads.user import UserPayload


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


type InteractionDataPayload = (
    InvokedApplicationCommandPayload | ComponentResponsePayload
)
type AuthorizingIntegrationOwnersDict = dict[Literal[0, 1], Snowflake | Literal[0]]


class InteractionPayload(TypedDict, total=False):
    id: Required[Snowflake]
    application_id: Required[Snowflake]
    type: Required[Literal[1, 2, 3, 4, 5]]
    data: Required[
        InteractionDataPayload
    ]  # We won't be recieving PING (1) type interactions
    guild: GuildPayload
    guild_id: Snowflake
    channel: PartialGuildChannelPayload | PartialThreadPayload | PrivateChannelPayload
    channel_id: Required[Snowflake]
    member: MemberPayload
    user: UserPayload
    token: Required[str]
    version: Required[Literal[1]]
    message: MessagePayload
    app_permissions: Required[Permissions]
    locale: Required[str]
    guild_locale: str
    # skippinf entitlements as of now
    authorizing_integration_owners: Required[AuthorizingIntegrationOwnersDict]
    context: Required[Literal[0, 1, 2]]
    attachment_size_limit: Required[int]


class InteractionCallbackDataPayload(TypedDict, total=False):
    tts: bool
    content: str
    embeds: list[EmbedPayload]
    allowed_mentions: AllowedMentionsPayload
    flags: int
    components: list[UNIMPLEMENTED]
    attachments: list[FileUploadPayload]
    poll: UNIMPLEMENTED


class InteractionWebhookMessagePayload(TypedDict, total=False):
    content: str | None
    tts: bool | None
    embeds: list[EmbedPayload] | None
    allowed_mentions: AllowedMentionsPayload | None
    flags: int | None
    components: list[UNIMPLEMENTED] | None
    # unimplemented files
    attachments: list[FileUploadPayload] | None
    poll: UNIMPLEMENTED | None


class InteractionResponseCallbackPayload(TypedDict, total=False):
    type: Literal[1, 4, 5, 6, 7, 8, 9, 10, 12]
    data: InteractionCallbackDataPayload
