from typing import TYPE_CHECKING

from mizuki.enums.components import ComponentType
from mizuki.objects.components.button import ButtonResponse
from mizuki.objects.components.modal_child import (
    TextInputResponse,
    FileUploadResponse,
    RadioGroupResponse,
    CheckboxGroupResponse,
    CheckboxResponse,
)
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
    from mizuki.objects.resolveddata import ResolvedData

BASIC_COMPONENT_MAP: dict[ComponentType, type[ComponentResponse]] = {
    ComponentType.BUTTON: ButtonResponse,
    ComponentType.STRING_SELECT: StringSelectResponse,
    ComponentType.TEXT_INPUT: TextInputResponse,
    ComponentType.RADIO_GROUP: RadioGroupResponse,
    ComponentType.CHECKBOX_GROUP: CheckboxGroupResponse,
    ComponentType.CHECKBOX: CheckboxResponse,
}

OBJECT_CONTAINING_COMPONENT_MAP: dict[ComponentType, type[ComponentResponse]] = {
    ComponentType.FILE_UPLOAD: FileUploadResponse,
}

OBJECT_AND_STATE_CONTAINING_COMPONENT_MAP: dict[
    ComponentType, type[ComponentResponse]
] = {
    ComponentType.USER_SELECT: UserSelectResponse,
    ComponentType.ROLE_SELECT: RoleSelectResponse,
    ComponentType.MENTIONABLE_SELECT: MentionableSelectResponse,
    ComponentType.CHANNEL_SELECT: ChannelSelectResponse,
}


def parse_component_response(
    data: ComponentResponsePayload,
    *,
    resolved_data: ResolvedData | None = None,
    state: ConnectionState | None = None,
) -> ComponentResponse:
    if (
        resolved_component_type := (data.get("component_type") or data.get("type"))
    ) is None:
        raise ValueError(
            "Recieved a malformed component response. Could not find the component type."
        )

    component_type = ComponentType(resolved_component_type)

    if component_type is ComponentType.LABEL:
        if (component_data := data.get("component")) is None or (
            child_type := component_data.get("type")
        ) is None:
            raise ValueError(f"Recieved malformed label component in a response.")

        component_type = ComponentType(child_type)
        data = component_data

    if resp_object := BASIC_COMPONENT_MAP.get(component_type):
        return resp_object(data)  # type: ignore # This is resolved properly

    if resp_object := OBJECT_CONTAINING_COMPONENT_MAP.get(component_type):
        return resp_object(data, resolved_data=resolved_data)  # type: ignore # This is resolved properly.

    if resp_object := OBJECT_AND_STATE_CONTAINING_COMPONENT_MAP.get(component_type):
        return resp_object(data, resolved_data=resolved_data, state=state)  # type: ignore # This is resolved properly

    raise TypeError(
        f"Component of type {component_type.value} does not support interactions yet."
    )
