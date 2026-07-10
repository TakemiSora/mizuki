from typing import Literal, NotRequired, Required, TypedDict

from mizuki.payloads._types import Snowflake
from mizuki.payloads.emoji import PartialEmojiPayload


class BaseComponentPayload(TypedDict):
    type: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 21, 22, 23]
    id: NotRequired[int]


class ButtonPayload(BaseComponentPayload, total=False):
    type: Required[Literal[2]]
    style: Required[Literal[1, 2, 3, 4, 5, 6]]
    label: str
    emoji: PartialEmojiPayload
    custom_id: str
    sku_id: Snowflake
    url: str
    disabled: bool


class BaseSelectPayload(BaseComponentPayload, total=False):
    type: Required[Literal[3, 5, 6, 7, 8]]
    custom_id: str
    placeholder: str
    min_values: int
    max_values: int
    required: bool
    disabled: bool


class StringOptionPayload(TypedDict, total=False):
    label: Required[str]
    value: Required[str]
    description: str
    emoji: PartialEmojiPayload
    default: bool


class StringSelectPayload(BaseSelectPayload):
    type: Literal[3]
    options: list[StringOptionPayload]


class DefaultSelectOptionPayload(TypedDict):
    id: Snowflake
    type: Literal["role", "user", "channel"]


class ObjectSelectPayload(BaseSelectPayload):
    default_options: list[DefaultSelectOptionPayload]


class UserSelectPayload(ObjectSelectPayload):
    type: Literal[5]


class RoleSelectPayload(ObjectSelectPayload):
    type: Literal[6]


class MentionableSelectPayload(ObjectSelectPayload):
    type: Literal[7]


class ChannelSelectPayload(ObjectSelectPayload):
    type: Literal[8]
    channel_types: Literal[0, 1, 2, 4, 5, 10, 11, 12, 13, 14, 15, 16]


type ActionRowChildComponent = (
    ButtonPayload
    | StringSelectPayload
    | UserSelectPayload
    | RoleSelectPayload
    | MentionableSelectPayload
    | ChannelSelectPayload
)


class ActionRowPayload(BaseComponentPayload):
    type: Literal[1]
    components: list[ActionRowChildComponent]


class TextInputPayload(BaseComponentPayload, total=False):
    type: Required[Literal[4]]
    custom_id: Required[str]
    style: Required[Literal[0, 1]]
    min_length: int
    max_length: int
    required: bool
    value: str
    placeholder: str


class UnfurledMediaItem(TypedDict, total=False):
    url: Required[str]
    proxy_url: str
    height: int | None
    width: int | None
    placeholder: str
    placeholder_version: int
    content_type: str
    flags: int
    attachment_id: Snowflake


class TextDisplayPayload(BaseComponentPayload):
    type: Literal[10]
    content: str


class ThumbnailPayload(BaseComponentPayload):
    type: Literal[11]
    media: UnfurledMediaItem
    description: str
    spoiler: bool


# Currently limited to only these, until discord adds more support
type SectionChildComponent = TextDisplayPayload
type SectionAccessoryComponent = ButtonPayload | ThumbnailPayload


class SectionPayload(BaseComponentPayload):
    type: Literal[9]
    components: list[SectionChildComponent]
    accessory: SectionAccessoryComponent


class MediaGalleryItemPayload(TypedDict, total=False):
    media: Required[UnfurledMediaItem]
    description: str
    spoiler: bool


class MediaGalleryPayload(BaseComponentPayload):
    type: Literal[12]
    items: list[MediaGalleryItemPayload]


class FileComponentPayload(BaseComponentPayload, total=False):
    type: Required[Literal[13]]
    file: Required[UnfurledMediaItem]
    spoiler: bool
    name: str
    size: int


class SeparatorPayload(BaseComponentPayload, total=False):
    type: Required[Literal[14]]
    divider: bool
    spacing: Literal[1, 2]


type ContainerChildComponent = (
    ActionRowPayload
    | TextDisplayPayload
    | SectionPayload
    | MediaGalleryPayload
    | SeparatorPayload
    | FileComponentPayload
)


class ContainerPayload(BaseComponentPayload, total=False):
    type: Required[Literal[17]]
    components: list[ContainerChildComponent]
    accent_color: int | None
    spoiler: bool


class FileUploadPayload(BaseComponentPayload, total=False):
    type: Required[Literal[19]]
    custom_id: Required[str]
    min_values: int
    max_values: int
    required: bool


class RadioGroupOptionPayload(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class RadioGroupPayload(BaseComponentPayload):
    type: Literal[21]
    custom_id: str
    options: list[RadioGroupOptionPayload]
    required: NotRequired[bool]


class CheckboxGroupOptionPayload(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class CheckboxGroupPayload(BaseComponentPayload):
    type: Literal[22]
    custom_id: str
    options: list[CheckboxGroupOptionPayload]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: bool


class CheckboxPayload(BaseComponentPayload):
    type: Literal[23]
    custom_id: str
    default: NotRequired[bool]


type LabelChildComponent = (
    TextInputPayload
    | StringSelectPayload
    | UserSelectPayload
    | MentionableSelectPayload
    | ChannelSelectPayload
    | RadioGroupPayload
)


class LabelPayload(BaseComponentPayload):
    type: Literal[18]
    label: str
    description: NotRequired[str]
    component: LabelChildComponent
