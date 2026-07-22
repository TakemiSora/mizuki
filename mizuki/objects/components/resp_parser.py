from typing import TYPE_CHECKING

from mizuki.enums.components import ComponentType
from mizuki.objects.components.button import ButtonResponse
from mizuki.objects.components.objectselect import (
    ChannelSelectResponse,
    MentionableSelectResponse,
    RoleSelectResponse,
    UserSelectResponse,
)
from mizuki.objects.components.stringselect import StringSelectResponse

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.payloads.components import ComponentResponsePayload
    from mizuki.objects.components import ComponentResponse

type BasicComponent = ButtonResponse | StringSelectResponse

BASIC_COMPONENT_MAP: dict[ComponentType, type[BasicComponent]] = {
    ComponentType.BUTTON: ButtonResponse,
    ComponentType.STRING_SELECT: StringSelectResponse,
}

type ObjectContainingComponent = (
    UserSelectResponse
    | RoleSelectResponse
    | MentionableSelectResponse
    | ChannelSelectResponse
)

OBJECT_CONTAINING_COMPONENT_MAP: dict[
    ComponentType, type[ObjectContainingComponent]
] = {
    ComponentType.USER_SELECT: UserSelectResponse,
    ComponentType.ROLE_SELECT: RoleSelectResponse,
    ComponentType.MENTIONABLE_SELECT: MentionableSelectResponse,
    ComponentType.CHANNEL_SELECT: ChannelSelectResponse,
}


def parse_component_response(
    data: ComponentResponsePayload, *, guild_id: int | None, state: ConnectionState
) -> ComponentResponse:
    component_type = ComponentType(data["component_type"])

    if resp_object := BASIC_COMPONENT_MAP.get(component_type):
        return resp_object(data)  # type: ignore # This is resolved properly

    if resp_object := OBJECT_CONTAINING_COMPONENT_MAP.get(component_type):
        return resp_object(data, guild_id=guild_id, state=state)  # type: ignore # This is resolved properly

    raise TypeError(
        f"Component of type {component_type.value} does not support interactions yet."
    )
