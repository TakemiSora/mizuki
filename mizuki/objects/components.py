from __future__ import annotations
from typing import Literal, Self, overload

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, mtd, scls, _MISSING
from mizuki.enums.components import ButtonStyle, ComponentType, DefaultSelectValueType
from mizuki.objects.emoji import PartialEmoji
from mizuki.objects.snowflake import Snowflake
from mizuki.payloads.components import (
    ActionRowChildComponentPayload,
    BaseComponentPayload,
    BaseSelectPayload,
    ButtonPayload,
    ActionRowPayload,
    ComponentTypeLiteral,
    DefaultSelectValuePayload,
    ObjectSelectPayload,
    SelectTypeLiteral,
    StringOptionPayload,
    StringSelectPayload,
    ObjectSelectTypeLiteral,
)

__all__ = (
    "Button",
    "StringOption",
    "StringSelect",
    "DefaultSelectValue",
    "UserSelect",
    "RoleSelect",
    "MentionableSelect",
    "ActionRow",
    "Component",
)


class BaseComponent:
    __slots__ = ("id", "type")

    type: ComponentType
    "The type of the component."

    id: int | None
    "An optional identifier for the component."

    def __init__[T: ComponentTypeLiteral](self, data: BaseComponentPayload[T]):
        self.type = ComponentType(data["type"])
        self.id = data.get("id")

    def _to_dict(self):
        raise NotImplementedError()


class Button(BaseComponent):
    """
    Represents a Button Component.
    """

    __slots__ = ("style", "label", "emoji", "custom_id", "sku_id", "url", "disabled")

    style: ButtonStyle
    "The style of the button."

    label: str | None
    "The label of the button."

    emoji: PartialEmoji | None
    "The emoji of the button."

    custom_id: str | None
    "The Custom ID of the button. Always present on non-link and non-premium buttons."

    sku_id: Snowflake | None
    "The Sku ID of the item. Only present on Premium Style Buttons."

    url: str | None
    "The URL the button leads to. Only present on Link Style Buttons."

    disabled: bool
    "Whether the button is disabled."

    def __init__(self, data: ButtonPayload):
        super().__init__(data)

        self.style = ButtonStyle(data["style"])
        self.label = data.get("label")
        self.emoji = scls(PartialEmoji, data.get("emoji"))
        self.custom_id = data.get("custom_id")
        self.sku_id = scls(Snowflake, data.get("sku_id"))
        self.url = data.get("url")
        self.disabled = data.get("disabled", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": self.type.value,
                "style": self.style.value,
                "disabled": self.disabled,
            },
            id=self.id,
            type=self.type.value,
            style=self.style.value,
            label=self.label,
            emoji=mtd(self.emoji),
            custom_id=self.custom_id,
            sku_id=self.sku_id,
            url=self.url,
            disabled=self.disabled,
        )

    @overload
    @classmethod
    def new(
        cls,
        label: str = _MISSING,
        *,
        style: Literal[
            ButtonStyle.PRIMARY,
            ButtonStyle.SECONDARY,
            ButtonStyle.SUCCESS,
            ButtonStyle.DANGER,
        ],
        id: int = _MISSING,
        emoji: PartialEmoji = _MISSING,
        custom_id: str,
        disabled: bool = False,
    ) -> Button: ...

    @overload
    @classmethod
    def new(
        cls,
        label: str = _MISSING,
        *,
        style: Literal[ButtonStyle.LINK],
        id: int = _MISSING,
        emoji: PartialEmoji = _MISSING,
        url: str,
    ) -> Button: ...

    @classmethod
    def new(
        cls,
        label: str = _MISSING,
        *,
        style: ButtonStyle,
        id: int = _MISSING,
        emoji: PartialEmoji = _MISSING,
        custom_id: str = _MISSING,
        sku_id: int = _MISSING,
        url: str = _MISSING,
        disabled: bool = False,
    ) -> Button:
        """
        Creates a new button instance.

        Parameters
        ----------
        label : :class:`str`, optional
            The label of the button.

        style : :class:`ButtonStyle <mizuki.enums.components.ButtonStyle>`
            The style of the button.

        id : :class:`int`, optional
            Optional unique identifier for the button.

        emoji : :class:`PartialEmoji <mizuki.objects.emoji.PartialEmoji>`, optional
            The emoji shown for the button.

        custom_id : :class:`str`, optional
            The custom ID of the button. Must be provided for non-link and non-premium buttons.

        sku_id : :class:`int`, optional
            The Sku ID of the related item. Must only be provided for premium buttons.

        url : :class:`str`, optional
            The URL the button redirects to. Must only be provided for link buttons.

        disabled : :class:`bool`, optional
            Whether the button is disabled.
        """
        return assign_val(
            cls({"type": 2, "style": style.value}),
            label=label,
            id=id,
            emoji=emoji,
            custom_id=custom_id,
            sku_id=sku_id,
            url=url,
            disabled=disabled,
        )


class BaseSelect(BaseComponent):
    __slots__ = (
        "custom_id",
        "placeholder",
        "min_values",
        "max_values",
        "required",
        "disabled",
    )

    custom_id: str
    "The Custom ID of the Select component."

    placeholder: str | None
    "The placeholder of the Select component."

    min_values: int | None
    "The minimum amount of values that can be selected."

    max_values: int | None
    "The maximum amount of values that can be selected."

    required: bool
    "Whether this Select is required. Only applicable to modals."

    disabled: bool
    "Whether this Select is required. Only applicable to messages."

    def __init__[T: SelectTypeLiteral](self, data: BaseSelectPayload[T]):
        super().__init__(data)

        self.custom_id = data["custom_id"]
        self.placeholder = data.get("placeholder")
        self.min_values = data.get("min_values")
        self.max_values = data.get("max_values")
        self.required = data.get("required", True)
        self.disabled = data.get("disabled", False)


class StringOption:
    """
    Represents a StringOption object to be used as options in :class:`StringSelect <mizuki.objects.components.StringSelect>`.
    """

    __slots__ = ("label", "value", "description", "emoji", "default")

    label: str
    "The label shown for this option."

    value: str
    "The value of this option."

    description: str | None
    "The description shown for this option."

    emoji: PartialEmoji | None
    "The emoji shown for this option."

    default: bool
    "Whether this option is selected by default."

    def __init__(self, data: StringOptionPayload):
        self.label = data["label"]
        self.value = data["value"]
        self.description = data.get("description")
        self.emoji = scls(PartialEmoji, data.get("emoji"))
        self.default = data.get("default", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"label": self.label, "value": self.value},
            description=self.description,
            emoji=mtd(self.emoji),
            default=self.default or None,
        )

    @classmethod
    def new(
        cls,
        *,
        label: str,
        value: str,
        description: str = _MISSING,
        emoji: PartialEmoji = _MISSING,
        default: bool = False,
    ) -> StringOption:
        """
        Creates a new instance of StringOption.

        Parameters
        ----------
        label : :class:`str`
            The label shown for this option.

        value : :class:`str`
            The value that is selected with this option.

        description : :class:`str`, optional
            The description shown for this option.

        emoji : :class:`PartialEmoji <mizuki.objects.emoji.PartialEmoji>`, optional
            The emoji shown for this option.

        default : :class:`bool`, optional
            Whether this option is selected by default in this Select.
            Only one component per select option may have this set to True.
        """
        return assign_val(
            cls({"label": label, "value": value, "default": default}),
            emoji=emoji,
            description=description,
        )


class StringSelect(BaseSelect):
    """
    Represents a StringSelect component.
    """

    __slots__ = ("options",)

    options: list[StringOption]
    "The options for this Select component."

    def __init__(self, data: StringSelectPayload):
        super().__init__(data)

        self.options = [StringOption(d) for d in data["options"]]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": 3,
                "custom_id": self.custom_id,
                "options": [o._to_dict() for o in self.options],
            },
            id=self.id,
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
            required=self.required if self.required is not True else None,
            disabled=self.disabled or None,
        )

    @classmethod
    def new(
        cls,
        *,
        options: list[StringOption],
        custom_id: str,
        id: int = _MISSING,
        placeholder: str = _MISSING,
        min_values: int = _MISSING,
        max_values: int = _MISSING,
        required: bool = True,
        disabled: bool = False,
    ) -> StringSelect:
        """
        Creates a new StringSelect instance.

        Parameters
        ----------
        options : list[:class:`StringOption <mizuki.objects.components.StringOption>`]
            The options for the StringSelect.

        custom_id : :class:`str`
            The custom ID of the StringSelect.

        id : :class:`int`, optional
            Optional Unique identifier for the StringSelect.

        placeholder : :class:`str`, optional
            The placeholder string shown on the StringSelect.

        min_values : :class:`int`, optional
            The minimum amount of values the user has to select.

        max_values : :class:`int`, optional
            The maximum amount of values the user can select.

        required : :class:`bool`, optional
            Whether this StringSelect is required in modals.

        disabled : :class:`bool`, optional
            Whether this StringSelect is disabled in messages.
        """
        return assign_val(
            cls({"type": 3, "custom_id": custom_id, "options": []}),
            options=options,
            id=id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            required=required,
            disabled=disabled,
        )


class DefaultSelectValue:
    __slots__ = ("id", "type")

    def __init__(self, data: DefaultSelectValuePayload):
        self.id = Snowflake(data["id"])
        self.type = DefaultSelectValueType(data["type"])

    def _to_dict(self) -> JSONPayload:
        return {"id": self.id, "type": self.type.value}

    @classmethod
    def new(cls, id: int, *, type: DefaultSelectValueType) -> DefaultSelectValue:
        return assign_val(cls.__new__(cls), id=Snowflake(id), type=type)


class ObjectSelect[
    T: ObjectSelectTypeLiteral,
    DefaultOptionParam: int | DefaultSelectValue,
](BaseSelect):
    __slots__ = ("default_values",)

    def __init__(self, data: ObjectSelectPayload[T]):
        super().__init__(data)

        self.default_values = [
            DefaultSelectValue(d) for d in data.get("default_values", [])
        ]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": self.type.value,
                "custom_id": self.custom_id,
            },
            id=self.id,
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
            default_values=[d._to_dict() for d in self.default_values],
            required=self.required if self.required is not True else None,
            disabled=self.disabled or None,
        )

    @classmethod
    def new(
        cls,
        *,
        custom_id: str,
        id: int = _MISSING,
        placeholder: str = _MISSING,
        min_values: int = _MISSING,
        max_values: int = _MISSING,
        default_values: list[DefaultOptionParam] = _MISSING,
        required: bool = True,
        disabled: bool = False,
    ) -> Self:
        """
        Creates a new Select instance.

        Parameters
        ----------
        custom_id : :class:`str`
            The custom ID of the Select.

        id : :class:`int`, optional
            Optional Unique identifier for the Select.

        placeholder : :class:`str`, optional
            The placeholder string shown on the Select.

        min_values : :class:`int`, optional
            The minimum amount of values the user has to select.

        max_values : :class:`int`, optional
            The maximum amount of values the user can select.

        default_values : list[:class:`int` | :class:`DefaultSelectOption <mizuki.objects.components.DefaultSelectOption>`]
            The options that are selected by default on this select.

        required : :class:`bool`, optional
            Whether this Select is required in modals.

        disabled : :class:`bool`, optional
            Whether this Select is disabled in messages.
        """
        if _MISSING not in (
            component_type := getattr(cls, "_TYPE", _MISSING),
            default_type := getattr(cls, "_DEFAULT_OPTION_TYPE", _MISSING),
        ):
            if default_values:
                if default_type is None:
                    raise ValueError(
                        "Cannot auto convert integer IDs to DefaultSelectOption in MentionableSelect."
                    )

                default_values = [
                    DefaultSelectValue.new(i, type=default_type)
                    if isinstance(i, int)
                    else i
                    for i in default_values
                ]

            return assign_val(
                cls(
                    {
                        "type": component_type,
                        "custom_id": custom_id,
                    }
                ),
                id=id,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                default_values=default_values,
                required=required,
                disabled=disabled,
            )

        raise NotImplementedError("'ObjectSelect' does not implement construction.")


class UserSelect(ObjectSelect[Literal[5], int | DefaultSelectValue]):
    _TYPE = 5
    _DEFAULT_OPTION_TYPE = DefaultSelectValueType.USER


class RoleSelect(ObjectSelect[Literal[6], int | DefaultSelectValue]):
    _TYPE = 6
    _DEFAULT_OPTION_TYPE = DefaultSelectValueType.ROLE


class MentionableSelect(ObjectSelect[Literal[7], DefaultSelectValue]):
    _TYPE = 7
    _DEFAULT_OPTION_TYPE = None


type ActionRowChildComponent = (
    Button | StringSelect | UserSelect | RoleSelect | MentionableSelect
)

ACTIONROW_CHILD_MAP: dict[ComponentType, type[ActionRowChildComponent]] = {
    ComponentType.BUTTON: Button,
    ComponentType.STRING_SELECT: StringSelect,
    ComponentType.USER_SELECT: UserSelect,
    ComponentType.ROLE_SELECT: RoleSelect,
    ComponentType.MENTIONABLE_SELECT: MentionableSelect,
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


type Component = ActionRow | Button | StringSelect | UserSelect | RoleSelect | MentionableSelect
