from __future__ import annotations
from typing import TYPE_CHECKING

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, _MISSING
from mizuki.objects.components._types import BaseComponent
from mizuki.objects.components.button import Button
from mizuki.objects.components.stringselect import StringSelect
from mizuki.objects.components.objectselect import (
    UserSelect,
    RoleSelect,
    MentionableSelect,
    ChannelSelect,
)
from mizuki.enums.components import ComponentType

if TYPE_CHECKING:
    from mizuki.payloads.components import (
        ActionRowChildComponentPayload,
        ActionRowPayload,
    )

__all__ = ("ActionRow",)

type ActionRowChildComponent = (
    Button | StringSelect | UserSelect | RoleSelect | MentionableSelect | ChannelSelect
)

ACTIONROW_CHILD_MAP: dict[ComponentType, type[ActionRowChildComponent]] = {
    ComponentType.BUTTON: Button,
    ComponentType.STRING_SELECT: StringSelect,
    ComponentType.USER_SELECT: UserSelect,
    ComponentType.ROLE_SELECT: RoleSelect,
    ComponentType.MENTIONABLE_SELECT: MentionableSelect,
    ComponentType.CHANNEL_SELECT: ChannelSelect,
}


def parse_action_row_child(
    data: ActionRowChildComponentPayload,
) -> ActionRowChildComponent:
    component_type = ComponentType(data["type"])

    try:
        return ACTIONROW_CHILD_MAP[component_type](data)  # type: ignore # This is resolved to be the correct match
    except KeyError:
        raise TypeError(
            f"Component of type {component_type.value} cannot be inserted into an ActionRow."
        )


class ActionRow(BaseComponent):
    __slots__ = ("components",)

    def __init__(self, data: ActionRowPayload):
        super().__init__(data)

        self.components = [parse_action_row_child(d) for d in data["components"]]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 1},
            id=self.id,
            components=[c._to_dict() for c in self.components],
        )

    @classmethod
    def new(cls, components: list[ActionRowChildComponent], *, id: int = _MISSING):
        return assign_val(
            cls({"type": 1, "components": []}), id=id, components=components
        )

    def add(
        self,
        components: list[ActionRowChildComponent] | ActionRowChildComponent,
    ) -> ActionRow:
        if isinstance(components, list):
            self.components += components
        else:
            self.components.append(components)

        return self
