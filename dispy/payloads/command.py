from __future__ import annotations
from typing import Literal, NotRequired, Required, TypedDict

from ._types import Permissions, Snowflake

LocalizationPayload = TypedDict("LocalizationPayload", {
    "id": str,
    "da": str,
    "de": str,
    "en-GB": str,
    "en-US": str,
    "es-ES": str,
    "es-419": str,
    "fr": str,
    "hr": str,
    "it": str,
    "lt": str,
    "hu": str,
    "nl": str,
    "no": str,
    "pl": str,
    "pt-BR": str,
    "ro": str,
    "fi": str,
    "sv-SE": str,
    "vi": str,
    "tr": str,
    "cs": str,
    "el": str,
    "bg": str,
    "ru": str,
    "uk": str,
    "hi": str,
    "th": str,
    "zh-CN": str,
    "ja": str,
    "zh-TW": str,
    "ko": str,
})

class CommandChoicePayload(TypedDict):
    name: str
    name_localizations: NotRequired[LocalizationPayload | None]
    value: str | int | float

class CommandOptionPayload(TypedDict, total=False):
    type: Required[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
    name: Required[str]
    name_localizations: LocalizationPayload | None
    description: Required[str]
    description_localizations: LocalizationPayload | None
    required: bool
    choices: list[CommandChoicePayload]
    options: list[CommandOptionPayload]
    channel_types: list[Literal[0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16]]
    min_value: int | float
    max_value: int | float
    min_length: int
    max_length: int
    autocomplete: bool

class ApplicationCommandPayload(TypedDict, total=False):
    id: Required[Snowflake]
    type: Literal[1, 2, 3, 4]
    application_id: Required[Snowflake]
    guild_id: Snowflake
    name: Required[str]
    name_localizations: LocalizationPayload | None
    description: Required[str]
    description_localizations: LocalizationPayload | None
    options: list[CommandOptionPayload]
    default_member_permissions: Required[Permissions | None]
    nsfw: bool
    integration_types: list[Literal[0, 1]]
    contexts: list[Literal[0, 1, 2]] | None
    version: Snowflake
    handler: Literal[1, 2]