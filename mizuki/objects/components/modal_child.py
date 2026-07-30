from typing import TYPE_CHECKING

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, _MISSING
from mizuki.enums.components import ComponentType
from mizuki.objects.components.common import BaseComponent, component_parser_gen
from mizuki.objects.components.objectselect import (
    ChannelSelect,
    MentionableSelect,
    RoleSelect,
    UserSelect,
)
from mizuki.objects.components.stringselect import StringSelect
from mizuki.objects.components.textinput import TextInput

if TYPE_CHECKING:
    from mizuki.payloads.components import LabelPayload

__all__ = ("Label",)

type LabelChildComponent = (
    TextInput
    | StringSelect
    | UserSelect
    | RoleSelect
    | MentionableSelect
    | ChannelSelect
)

LABEL_CHILD_MAP: dict[ComponentType, type[LabelChildComponent]] = {
    ComponentType.TEXT_INPUT: TextInput,
    ComponentType.STRING_SELECT: StringSelect,
    ComponentType.USER_SELECT: UserSelect,
    ComponentType.ROLE_SELECT: RoleSelect,
    ComponentType.MENTIONABLE_SELECT: MentionableSelect,
    ComponentType.CHANNEL_SELECT: ChannelSelect,
}

parse_label_child = component_parser_gen(LABEL_CHILD_MAP, "Label")


class Label(BaseComponent):
    """Represents a Label component."""

    __slots__ = ("label", "description", "component")

    label: str
    "The text of the label."

    description: str | None
    "The description of the label."

    component: LabelChildComponent
    "The component the label is wrapped on."

    def __init__(self, data: LabelPayload) -> None:
        super().__init__(data)

        self.label = data["label"]
        self.description = data.get("description")
        self.component = parse_label_child(data["component"])

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 18, "label": self.label, "component": self.component._to_dict()},
            id=self.id,
            description=self.description,
        )

    @classmethod
    def new(
        cls,
        component: LabelChildComponent,
        *,
        label: str,
        description: str = _MISSING,
        id: int = _MISSING,
    ) -> Label:
        """Returns an instance of a Label component.

        Parameters
        ----------
        component : :type:`LabelChildComponent`
            The component the label will be wrapped around.

        label : :class:`str`
            The text of the label.

        description : :class:`str`, optional
            The description of the label.

        id : :class:`int`, optional
            Optional unique identifier for the component.
        """
        return assign_val(
            cls(
                {
                    "type": 18,
                    "label": label,
                    "component": component._to_dict(),
                },
            ),
            description=description,
            id=id,
        )
