from typing import Literal, NotRequired, Required, TypedDict

from mizuki.payloads._types import Snowflake
from mizuki.payloads.emoji import PartialEmojiPayload
from mizuki.payloads.interaction import ResolvedDataPayload

type ComponentTypeLiteral = Literal[
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 21, 22, 23
]


class BaseComponentPayload[T: ComponentTypeLiteral](TypedDict):
    type: T
    id: NotRequired[int]


class ButtonPayload(BaseComponentPayload[Literal[2]], total=False):
    style: Required[Literal[1, 2, 3, 4, 5, 6]]
    label: str
    emoji: PartialEmojiPayload
    custom_id: str
    sku_id: Snowflake
    url: str
    disabled: bool


type SelectTypeLiteral = Literal[3, 5, 6, 7, 8]


class BaseSelectPayload[T: SelectTypeLiteral](BaseComponentPayload[T], total=False):
    custom_id: Required[str]
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


class StringSelectPayload(BaseSelectPayload[Literal[3]]):
    options: list[StringOptionPayload]


class DefaultSelectValuePayload(TypedDict):
    id: Snowflake
    type: Literal["role", "user", "channel"]


type ObjectSelectTypeLiteral = Literal[5, 6, 7, 8]


class ObjectSelectPayload[T: ObjectSelectTypeLiteral](
    BaseSelectPayload[T], total=False
):
    default_values: list[DefaultSelectValuePayload]


type UserSelectPayload = ObjectSelectPayload[Literal[5]]

type RoleSelectPayload = ObjectSelectPayload[Literal[6]]

type MentionableSelectPayload = ObjectSelectPayload[Literal[7]]


class ChannelSelectPayload(ObjectSelectPayload[Literal[8]], total=False):
    channel_types: list[Literal[0, 1, 2, 4, 5, 10, 11, 12, 13, 14, 15, 16]]


type ActionRowChildComponentPayload = (
    ButtonPayload
    | StringSelectPayload
    | UserSelectPayload
    | RoleSelectPayload
    | MentionableSelectPayload
    | ChannelSelectPayload
)


class ActionRowPayload(BaseComponentPayload[Literal[1]]):
    components: list[ActionRowChildComponentPayload]


class TextInputPayload(BaseComponentPayload[Literal[4]], total=False):
    custom_id: Required[str]
    style: Required[Literal[0, 1]]
    min_length: int
    max_length: int
    required: bool
    value: str
    placeholder: str


class UnfurledMediaItemPayload(TypedDict, total=False):
    url: Required[str]
    proxy_url: str
    height: int | None
    width: int | None
    placeholder: str
    placeholder_version: int
    content_type: str
    flags: Literal[0, 1]
    attachment_id: Snowflake


class TextDisplayPayload(BaseComponentPayload[Literal[10]]):
    content: str


class ThumbnailPayload(BaseComponentPayload[Literal[11]], total=False):
    media: Required[UnfurledMediaItemPayload]
    description: str | None
    spoiler: bool


# Currently limited to only these, until discord adds more support
type SectionChildComponentPayload = TextDisplayPayload
type SectionAccessoryComponentPayload = ButtonPayload | ThumbnailPayload


class SectionPayload(BaseComponentPayload[Literal[9]]):
    components: list[SectionChildComponentPayload]
    accessory: SectionAccessoryComponentPayload


class MediaGalleryItemPayload(TypedDict, total=False):
    media: Required[UnfurledMediaItemPayload]
    description: str
    spoiler: bool


class MediaGalleryPayload(BaseComponentPayload[Literal[12]]):
    items: list[MediaGalleryItemPayload]


class FileComponentPayload(BaseComponentPayload[Literal[13]], total=False):
    file: Required[UnfurledMediaItemPayload]
    spoiler: bool
    name: str
    size: int


class SeparatorPayload(BaseComponentPayload[Literal[14]], total=False):
    divider: bool
    spacing: Literal[1, 2]


type ContainerChildComponentPayload = (
    ActionRowPayload
    | TextDisplayPayload
    | SectionPayload
    | MediaGalleryPayload
    | SeparatorPayload
    | FileComponentPayload
)


class ContainerPayload(BaseComponentPayload[Literal[17]], total=False):
    components: Required[list[ContainerChildComponentPayload]]
    accent_color: int | None
    spoiler: bool


class FileUploadPayload(BaseComponentPayload[Literal[19]], total=False):
    custom_id: Required[str]
    min_values: int
    max_values: int
    required: bool


class RadioGroupOptionPayload(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class RadioGroupPayload(BaseComponentPayload[Literal[21]]):
    custom_id: str
    options: list[RadioGroupOptionPayload]
    required: NotRequired[bool]


class CheckboxGroupOptionPayload(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class CheckboxGroupPayload(BaseComponentPayload[Literal[22]]):
    custom_id: str
    options: list[CheckboxGroupOptionPayload]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    required: bool


class CheckboxPayload(BaseComponentPayload[Literal[23]]):
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


class LabelPayload(BaseComponentPayload[Literal[18]]):
    label: str
    description: NotRequired[str]
    component: LabelChildComponent


type ComponentPayload = (
    ActionRowPayload
    | ButtonPayload
    | StringSelectPayload
    | TextInputPayload
    | UserSelectPayload
    | RoleSelectPayload
    | MentionableSelectPayload
    | ChannelSelectPayload
    | SectionPayload
    | TextDisplayPayload
    | ThumbnailPayload
    | MediaGalleryPayload
    | FileComponentPayload
    | SeparatorPayload
    | ContainerPayload
    | LabelPayload
    | FileUploadPayload
    | RadioGroupPayload
    | CheckboxGroupPayload
    | CheckboxPayload
)

type InteractiveComponentTypeLiteral = Literal[2, 3, 5, 6, 7, 8]


class BaseComponentResponsePayload[T: InteractiveComponentTypeLiteral](TypedDict):
    component_type: T
    custom_id: str
    id: NotRequired[int]


type ButtonResponsePayload = BaseComponentResponsePayload[Literal[2]]


class StringSelectResponsePayload(BaseComponentResponsePayload[Literal[3]]):
    values: list[str]


class ObjectSelectResponsePayload[T: ObjectSelectTypeLiteral](
    BaseComponentResponsePayload[T]
):
    resolved: ResolvedDataPayload
    values: list[Snowflake]


type UserSelectResponsePayload = ObjectSelectResponsePayload[Literal[5]]
type RoleSelectResponsePayload = ObjectSelectResponsePayload[Literal[6]]
type MentionableSelectResponsePayload = ObjectSelectResponsePayload[Literal[7]]
type ChannelSelectResponsePayload = ObjectSelectResponsePayload[Literal[8]]
