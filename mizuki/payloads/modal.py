from typing import TYPE_CHECKING, NotRequired, TypedDict

if TYPE_CHECKING:
    from mizuki.payloads.components import (
        ComponentResponsePayload,
        LabelPayload,
        TextDisplayPayload,
    )
    from mizuki.payloads.interaction import ResolvedDataPayload


type ModalChildComponentPayload = TextDisplayPayload | LabelPayload


class ModalPayload(TypedDict):
    custom_id: str
    title: str
    components: list[ModalChildComponentPayload]


class ModalResponsePayload(TypedDict):
    custom_id: str
    components: list[ComponentResponsePayload]
    resolved: NotRequired[ResolvedDataPayload]
