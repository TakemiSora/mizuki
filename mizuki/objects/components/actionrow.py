from __future__ import annotations

from typing import TYPE_CHECKING

from mizuki._utils import _MISSING, JSONPayload, assign_val, assign_val_dict
from mizuki.enums.components import ComponentType
from mizuki.objects.components.button import Button
from mizuki.objects.components.common import BaseComponent, component_parser_gen
from mizuki.objects.components.objectselect import (
    ChannelSelect,
    MentionableSelect,
    RoleSelect,
    UserSelect,
)
from mizuki.objects.components.stringselect import StringSelect

if TYPE_CHECKING:
    from mizuki.payloads.components import ActionRowPayload

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

parse_action_row_child = component_parser_gen(ACTIONROW_CHILD_MAP, "ActionRow")


class ActionRow(BaseComponent):
    """
    Represents an ActionRow component.
    """

    components: list[ActionRowChildComponent]
    "The components of the ActionRow."

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
    def new(cls, *components: ActionRowChildComponent, id: int = _MISSING) -> ActionRow:
        """
        Returns an instance of an ActionRow.

        Paramaters
        ----------
        *components : :type:`ActionRowChildComponent`
            The component(s) to add to the ActionRow.

        id : :class:`int`, optional
            Optional unique identifier for the ActionRow.
        """
        return assign_val(
            cls({"type": 1, "components": []}), id=id, components=list(components)
        )

    def add(self, *components: ActionRowChildComponent) -> None:
        """
        Add components to the ActionRow.

        Parameters
        ----------
        *components : :type:`ActionRowChildComponent`
            The component(s) to add to the ActionRow.
        """
        self.components += list(components)
