from typing import NotRequired, Required, TypedDict
from mizuki.payloads._types import ISO8601Timestamp


class EmbedFooterPayload(TypedDict, total=False):
    text: Required[str]
    icon_url: str
    proxy_icon_url: str


class EmbedMediaPayload(TypedDict, total=False):
    proxy_url: str
    height: int
    width: int
    content_type: str
    placeholder: str
    placeholder_version: int
    description: str
    flags: int


class EmbedImagePayload(EmbedMediaPayload):
    url: str


class EmbedVideoPayload(EmbedMediaPayload, total=False):
    url: str


class EmbedProviderPayload(TypedDict, total=False):
    name: str
    url: str


class EmbedAuthorPayload(TypedDict, total=False):
    name: Required[str]
    url: str
    icon_url: str
    proxy_icon_url: str


class EmbedFieldPayload(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class EmbedPayload(TypedDict, total=False):
    title: str
    type: str
    description: str
    url: str
    timestamp: ISO8601Timestamp
    color: int
    footer: EmbedFooterPayload
    image: EmbedImagePayload
    thumbnail: EmbedImagePayload
    video: EmbedVideoPayload
    provider: EmbedProviderPayload
    author: EmbedAuthorPayload
    fields: list[EmbedFieldPayload]
    flags: int
