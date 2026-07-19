from __future__ import annotations
from typing import TYPE_CHECKING

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, mtd, scls, _MISSING

from mizuki.objects.components.common import BaseSelect
from mizuki.objects.emoji import PartialEmoji

if TYPE_CHECKING:
    from mizuki.payloads.components import StringOptionPayload, StringSelectPayload

__all__ = ("StringOption", "StringSelect")


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
