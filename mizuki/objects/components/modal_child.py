from typing import TYPE_CHECKING

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, _MISSING, maybe_iter
from mizuki.enums.components import ComponentType
from mizuki.objects.components.common import (
    BaseComponent,
    BaseComponentResponse,
    component_parser_gen,
)
from mizuki.objects.components.objectselect import (
    ChannelSelect,
    MentionableSelect,
    RoleSelect,
    UserSelect,
)
from mizuki.objects.components.stringselect import StringSelect
from mizuki.objects.components.textinput import TextInput
from mizuki.public_utils import generate_custom_id

if TYPE_CHECKING:
    from mizuki.payloads.components import LabelPayload
    from mizuki.payloads.components import (
        RadioGroupOptionPayload,
        RadioGroupPayload,
        RadioGroupResponsePayload,
    )

__all__ = ("Label", "RadioGroupOption", "RadioGroupResponse", "RadioGroup")


class RadioGroupOption:
    """
    Represents an option for a radio group.
    """

    __slots__ = ("value", "label", "description", "default")

    value: str
    "The value that the option will send."

    label: str
    "The label of the option."

    description: str | None
    "The description of the option."

    default: bool
    "Whether this option will be selected by default."

    def __init__(self, data: RadioGroupOptionPayload):
        self.value = data["value"]
        self.label = data["label"]
        self.description = data.get("description")
        self.default = data.get("default", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"label": self.label, "value": self.value, "description": self.description},
            description=self.description,
            default=self.default or None,
        )

    @classmethod
    def new(
        cls,
        *,
        value: str,
        label: str,
        description: str = _MISSING,
        default: bool = False,
    ) -> RadioGroupOption:
        """
        Returns an instance of a Radio Group Option.

        Parameters
        ----------
        value : :class:`str`
            The value that the option will send when selected.

        label : :class:`str`
            The label of the option.

        description : :class:`str`, optional
            The description of the option. Max 100 characters.

        default : :class:`bool`, optional
            Whether this option is selected by default. Defaults to ``False``.
        """
        return assign_val(
            cls({"value": value, "label": label}),
            description=description,
            default=default,
        )


class RadioGroupResponse(BaseComponentResponse):
    """
    Represents a response from a radio group component.
    """

    __slots__ = "value"

    value: str | None
    "The value that was selected, ``None`` if no values were selected."

    def __init__(self, data: RadioGroupResponsePayload):
        super().__init__(data)

        self.value = data.get("value")


class RadioGroup(BaseComponent[RadioGroupResponse]):
    """
    Represents a Radio Group component.
    """

    __slots__ = ("custom_id", "options", "required")

    custom_id: str
    "The custom ID of this component."

    options: list[RadioGroupOption]
    "The options for this radio group."

    required: bool
    "Whether this component is required to submit."

    def __init__(self, data: RadioGroupPayload):
        super().__init__(data)
        self.custom_id = data["custom_id"]
        self.options = [RadioGroupOption(d) for d in data["options"]]
        self.required = data.get("required", True)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": 21,
                "custom_id": self.custom_id,
                "options": maybe_iter(self.options),
            },
            id=self.id,
            required=self.required and False,
        )

    @classmethod
    def new(
        cls,
        *options: RadioGroupOption,
        custom_id: str = _MISSING,
        required: bool = True,
        id: int = _MISSING,
    ) -> RadioGroup:
        """
        Returns an instance of a radio group.

        Parameters
        ----------
        *options : :class:`RadioGroupOption`
            The options for this radio group. Only one may have ``default`` set to ``True``.

        custom_id : :class:`str`, optional
            The custom ID for this component, auto-generated if not provided.

        required : :class:`bool`, optional
            Whether this component is required to submit in a modal, defaults to ``True``.

        id : :class:`int`, optional
            Optional Unique identifier for this component.
        """
        return assign_val(
            cls(
                {
                    "type": 21,
                    "custom_id": custom_id or generate_custom_id(),
                    "options": [],
                }
            ),
            options=options,
            required=required,
            id=id,
        )


type LabelChildComponent = (
    TextInput
    | StringSelect
    | UserSelect
    | RoleSelect
    | MentionableSelect
    | ChannelSelect
    | RadioGroup
)

LABEL_CHILD_MAP: dict[ComponentType, type[LabelChildComponent]] = {
    ComponentType.TEXT_INPUT: TextInput,
    ComponentType.STRING_SELECT: StringSelect,
    ComponentType.USER_SELECT: UserSelect,
    ComponentType.ROLE_SELECT: RoleSelect,
    ComponentType.MENTIONABLE_SELECT: MentionableSelect,
    ComponentType.CHANNEL_SELECT: ChannelSelect,
    ComponentType.RADIO_GROUP: RadioGroup,
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
