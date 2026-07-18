from __future__ import annotations
from typing import overload, Literal

from mizuki.objects.components._types import BaseComponent
from mizuki.objects.emoji import PartialEmoji
from mizuki.objects.snowflake import Snowflake
from mizuki.enums import ButtonStyle
from mizuki.payloads.components import ButtonPayload
from mizuki._utils import scls, assign_val_dict, assign_val, JSONPayload, mtd, _MISSING

__all__ = ("Button",)


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
