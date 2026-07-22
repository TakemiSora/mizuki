from __future__ import annotations
from typing import TYPE_CHECKING

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, _MISSING
from mizuki.objects.components.common import BaseComponent
from mizuki.enums.components import TextInputStyle

if TYPE_CHECKING:
    from mizuki.payloads.components import TextInputPayload

__all__ = ("TextInput",)


class TextInput(BaseComponent):
    __slots__ = (
        "custom_id",
        "style",
        "min_length",
        "max_length",
        "required",
        "value",
        "placeholder",
    )

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
            id=id,
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
        custom_id: str,
        id: int = _MISSING,
        style: TextInputStyle = TextInputStyle.SHORT,
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        value: str = _MISSING,
        placeholder: str = _MISSING,
    ) -> TextInput:
        """ "
        Returns a TextInput instance.

        Parameters
        ----------
        custom_id : :class:`str`
            The custom ID of the TextInput.

        id : :class:`int`, optional
            Optional unique identifier for the TextInput.

        style : :class:`TextInputStyle <mizuki.enums.components.TextInputStyle>`, optional
            The style of the TextInput.

        min_length : :class:`int`, optional
            The minimum length that the user can input.

        max_length : :class:`int`, optional
            The maximum length that the user csn input.

        value : :class:`str`, optional
            The default value of the TextInput.

        placeholder : :class:`str`, optional
            The placeholder string for the TextInput.
        """
        return assign_val(
            cls(
                {"type": 4, "custom_id": custom_id, "style": style.value},
            ),
            id=id,
            min_length=min_length,
            max_length=max_length,
            value=value,
            placeholder=placeholder,
        )
