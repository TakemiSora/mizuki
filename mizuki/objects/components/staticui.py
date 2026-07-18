from __future__ import annotations
from typing import TYPE_CHECKING

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, _MISSING
from mizuki.objects.components._types import BaseComponent

if TYPE_CHECKING:
    from mizuki.payloads.components import TextDisplayPayload

__all__ = ("TextDisplay",)


class TextDisplay(BaseComponent):
    __slots__ = ("content",)

    def __init__(self, data: TextDisplayPayload):
        super().__init__(data)

        self.content = data["content"]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict({"type": 10, "content": self.content}, id=id)

    @classmethod
    def new(cls, content: str, *, id: int = _MISSING) -> TextDisplay:
        """
        Returns a TextDisplay instance.

        Parameters
        ----------
        content : :class:`str`
            The content of the TextDisplay.

        id : :class:`int`, optional
            Optional unique identifier for the TextDisplay.
        """
        return assign_val(cls({"type": 10, "content": content}), id=id)
