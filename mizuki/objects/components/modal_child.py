from typing import TYPE_CHECKING, Self

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, _MISSING, maybe_iter
from mizuki.enums.components import ComponentType, TextInputStyle
from mizuki.objects.components.common import (
    BaseComponent,
    BaseComponentResponse,
    HasCallbackResponse,
    component_parser_gen,
)
from mizuki.objects.components.objectselect import (
    ChannelSelect,
    MentionableSelect,
    RoleSelect,
    UserSelect,
)
from mizuki.objects.components.stringselect import StringSelect
from mizuki.public_utils import generate_custom_id

if TYPE_CHECKING:
    from mizuki.payloads.components import (
        TextInputResponsePayload,
        TextInputPayload,
        GroupOptionPayload,
        RadioGroupResponsePayload,
        RadioGroupPayload,
        CheckboxGroupResponsePayload,
        CheckboxGroupPayload,
        CheckboxResponsePayload,
        CheckboxPayload,
        LabelPayload,
    )

__all__ = (
    "TextInputResponse",
    "TextInput",
    "RadioGroupOption",
    "RadioGroupResponse",
    "RadioGroup",
    "CheckboxGroupOption",
    "CheckboxGroupResponse",
    "CheckboxGroup",
    "CheckboxResponse",
    "Checkbox",
    "Label",
)


class TextInputResponse(BaseComponentResponse):
    """
    Represents a response from a text input component.
    """

    __slots__ = ("value",)

    value: str
    "The value that the user entered."

    def __init__(self, data: TextInputResponsePayload):
        super().__init__(data)

        self.value = data["value"]


class TextInput(BaseComponent, HasCallbackResponse[TextInputResponse]):
    """
    Represents a text input component.
    """

    __slots__ = (
        "custom_id",
        "style",
        "min_length",
        "max_length",
        "required",
        "value",
        "placeholder",
    )

    custom_id: str
    "The custom ID of the component."

    style: TextInputStyle
    "The style of the text input."

    min_length: int | None
    "The minimum amount of characters the user must enter to submit."

    max_length: int | None
    "The maximum amount of characters the user can enter."

    required: bool
    "Whether this component is required in a modal."

    value: str | None
    "The default value for this text input."

    placeholder: str | None
    "The placeholder text if the text box is empty."

    def __init__(self, data: TextInputPayload):
        super().__init__(data)

        self.custom_id = data["custom_id"]
        self.style = TextInputStyle(data["style"])
        self.min_length = data.get("min_length")
        self.max_length = data.get("max_length")
        self.required = data.get("required", True)
        self.value = data.get("value")
        self.placeholder = data.get("placeholder")

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 4, "custom_id": self.custom_id, "style": self.style.value},
            id=self.id,
            min_length=self.min_length,
            max_length=self.max_length,
            required=(self.required if self.required is not True else None),
            value=self.value,
            placeholder=self.placeholder,
        )

    @classmethod
    def new(
        cls,
        *,
        custom_id: str = _MISSING,
        id: int = _MISSING,
        style: TextInputStyle = TextInputStyle.SHORT,
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        required: bool = True,
        value: str = _MISSING,
        placeholder: str = _MISSING,
    ) -> TextInput:
        """ "
        Returns a TextInput instance.

        Parameters
        ----------
        custom_id : :class:`str`, optional
            The custom ID of the TextInput. Auto-generated if not provided.

        id : :class:`int`, optional
            Optional unique identifier for the TextInput.

        style : :class:`TextInputStyle <mizuki.enums.components.TextInputStyle>`, optional
            The style of the TextInput.

        min_length : :class:`int`, optional
            The minimum length that the user can input.

        max_length : :class:`int`, optional
            The maximum length that the user can input.

        required : :class:`bool`, optional
            Whether this field is required in modals.

        value : :class:`str`, optional
            The default value of the TextInput.

        placeholder : :class:`str`, optional
            The placeholder string for the TextInput.
        """
        return assign_val(
            cls(
                {
                    "type": 4,
                    "custom_id": custom_id or generate_custom_id(),
                    "style": style.value,
                },
            ),
            id=id,
            min_length=min_length,
            max_length=max_length,
            required=required,
            value=value,
            placeholder=placeholder,
        )


class BaseGroupOption:
    __slots__ = ("value", "label", "description", "default")

    value: str
    "The value that the option will send."

    label: str
    "The label of the option."

    description: str | None
    "The description of the option."

    default: bool
    "Whether this option will be selected by default."

    def __init__(self, data: GroupOptionPayload):
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
    ) -> Self:
        """
        Returns an instance of a Group Option.

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


class RadioGroupOption(BaseGroupOption):
    """
    Represents an option for a radio group.
    """

    __slots__ = ()


class RadioGroupResponse(BaseComponentResponse):
    """
    Represents a response from a radio group component.
    """

    __slots__ = "value"

    value: str | None
    "The value that was selected, ``None`` if no values were selected."

    def __init__(self, data: RadioGroupResponsePayload):
        super().__init__(data)

        self.value = data["value"]


class RadioGroup(BaseComponent, HasCallbackResponse[RadioGroupResponse]):
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


class CheckboxGroupOption(BaseGroupOption):
    """
    Represents an option in a checkbox group.
    """

    __slots__ = ()


class CheckboxGroupResponse(BaseComponentResponse):
    """
    Represents a response from a checkbox group component.
    """

    __slots__ = ("values",)

    values: list[str]
    "The values selected in the component."

    def __init__(self, data: CheckboxGroupResponsePayload):
        super().__init__(data)

        self.values = data["values"]


class CheckboxGroup(BaseComponent, HasCallbackResponse[CheckboxGroupResponse]):
    """
    Represents a checkbox group component.
    """

    __slots__ = ("custom_id", "options", "min_values", "max_values", "required")

    custom_id: str
    "The custom ID of this component."

    options: list[CheckboxGroupOption]
    "The options for this checkbox group."

    min_values: int | None
    "The minimum amount of values an user must select to submit this component."

    max_values: int | None
    "The maxmium amount of values an user can select at most when submitting this component."

    required: bool
    "Whether this component is required to submit."

    def __init__(self, data: CheckboxGroupPayload):
        super().__init__(data)

        self.custom_id = data["custom_id"]
        self.options = [CheckboxGroupOption(d) for d in data["options"]]
        self.min_values = data.get("min_values")
        self.max_values = data.get("max_values")
        self.required = data.get("required", True)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": 22,
                "custom_id": self.custom_id,
                "options": maybe_iter(self.options),
            },
            id=self.id,
            min_values=self.min_values,
            max_values=self.max_values,
            required=self.required and None,
        )

    @classmethod
    def new(
        cls,
        *options: CheckboxGroupOption,
        id: int = _MISSING,
        custom_id: str = _MISSING,
        min_values: int = _MISSING,
        max_values: int = _MISSING,
        required: bool = True,
    ) -> CheckboxGroup:
        return assign_val(
            cls(
                {
                    "type": 22,
                    "options": [],
                    "custom_id": custom_id or generate_custom_id(),
                }
            ),
            id=id,
            options=options,
            min_values=min_values,
            max_values=max_values,
            required=required and None,
        )


class CheckboxResponse(BaseComponentResponse):
    """
    Represents a response from a checkbox component.
    """

    __slots__ = ("value",)

    value: bool
    "The value of the checkbox selected."

    def __init__(self, data: CheckboxResponsePayload):
        super().__init__(data)

        self.value = data["value"]


class Checkbox(BaseComponent, HasCallbackResponse[CheckboxResponse]):
    """
    Represents a checkbox component.
    """

    __slots__ = ("custom_id", "default")

    custom_id: str
    "The custom ID for this component."

    default: bool
    "The value thats selected by default."

    def __init__(self, data: CheckboxPayload):
        super().__init__(data)

        self.custom_id = data["custom_id"]
        self.default = data.get("default", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 23, "custom_id": self.custom_id},
            id=self.id,
            default=self.default or None,
        )

    @classmethod
    def new(
        cls, *, custom_id: str = _MISSING, id: int = _MISSING, default: bool = False
    ) -> Checkbox:
        """
        Returns an instance of a checkbox component.

        Parameters
        ----------
        custom_id : :class:`str`, optional
            The custom ID for this component, auto-generated if not provided.

        id : :class:`int`, optional
            Optional unique identifier for this component.

        default : :class:`bool`, optional
            Whether this checkbox is set to ``True`` or ``False`` by default.
        """
        return assign_val(
            cls({"type": 23, "custom_id": custom_id or generate_custom_id()}),
            id=id,
            default=default,
        )


type LabelChildComponent = (
    TextInput
    | StringSelect
    | UserSelect
    | RoleSelect
    | MentionableSelect
    | ChannelSelect
    | RadioGroup
    | CheckboxGroup
    | Checkbox
)

LABEL_CHILD_MAP: dict[ComponentType, type[LabelChildComponent]] = {
    ComponentType.STRING_SELECT: StringSelect,
    ComponentType.TEXT_INPUT: TextInput,
    ComponentType.USER_SELECT: UserSelect,
    ComponentType.ROLE_SELECT: RoleSelect,
    ComponentType.MENTIONABLE_SELECT: MentionableSelect,
    ComponentType.CHANNEL_SELECT: ChannelSelect,
    ComponentType.RADIO_GROUP: RadioGroup,
    ComponentType.CHECKBOX_GROUP: CheckboxGroup,
    ComponentType.CHECKBOX: Checkbox,
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
