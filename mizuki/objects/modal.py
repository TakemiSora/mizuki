from __future__ import annotations
from collections.abc import Callable, Coroutine
import inspect
from typing import TYPE_CHECKING, Self, cast, Any

from mizuki._utils import JSONPayload, assign_val, maybe_iter, _MISSING
from mizuki.enums.components import ComponentType
from mizuki.objects.components.common import component_parser_gen
from mizuki.objects.components.modal_child import Label
from mizuki.objects.components.resp_parser import parse_component_response
from mizuki.objects.components.staticui import TextDisplay
from mizuki.objects.resolveddata import ResolvedData
from mizuki.public_utils import generate_custom_id

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.payloads.modal import ModalPayload, ModalResponsePayload
    from mizuki.objects.interaction import Interaction

__all__ = ("Modal",)

type ModalChildComponent = TextDisplay | Label

MODAL_CHILD_MAP: dict[ComponentType, type[ModalChildComponent]] = {
    ComponentType.TEXT_DISPLAY: TextDisplay,
    ComponentType.LABEL: Label,
}

parse_modal_child = component_parser_gen(MODAL_CHILD_MAP, "Modal")

__all__ = ("ModalResponse", "Modal")


class ModalResponse[*ResponseType]:
    """Represents a response recieved from a Modal."""

    __slots__ = ("custom_id", "components", "resolved")

    custom_id: str
    "The custom ID of the modal."

    components: tuple[*ResponseType]
    "The responses of components from the modal"

    resolved: ResolvedData
    "The resolved ID to objects map."

    def __init__(
        self,
        data: ModalResponsePayload,
        *,
        guild_id: int | None,
        state: ConnectionState,
    ) -> None:
        self.custom_id = data["custom_id"]

        self.resolved = ResolvedData(
            data.get("resolved", {}), guild_id=guild_id, state=state
        )

        self.components = cast(
            tuple[*ResponseType],
            tuple(
                parse_component_response(r, resolved_data=self.resolved)
                for r in data["components"]
            ),
        )


class Modal:
    """Represents a Discord Modal."""

    __slots__ = ("custom_id", "title", "components", "_callback")

    custom_id: str
    "The custom ID of the modal."

    title: str
    "The title of the modal."

    components: list[ModalChildComponent]
    "The components in the modal."

    def __init__(self, data: ModalPayload) -> None:
        self.custom_id = data["custom_id"]
        self.title = data["title"]
        self.components = [parse_modal_child(c) for c in data["components"]]

    def _to_dict(self) -> JSONPayload:
        return {
            "custom_id": self.custom_id,
            "title": self.title,
            "components": maybe_iter(self.components),
        }

    @classmethod
    def new(
        cls, *components: ModalChildComponent, title: str, custom_id: str = _MISSING
    ) -> Modal:
        """
        Returns an instance of a Modal.

        Parameters
        ----------
        *components : :type:`ModalChildComponent`
            The compoennts to add to the modal.

        title : :class:`str`
            The title of the modal.

        custom_id : :class:`str`
            The custom ID for this modal, auto-generated if not provided.
        """
        return assign_val(
            cls(
                {
                    "title": title,
                    "custom_id": custom_id or generate_custom_id(),
                    "components": [],
                }
            ),
            components=list(components),
        )

    def set_callback(
        self, callback: Callable[[Interaction, ModalResponse], Coroutine[Any, Any, Any]]
    ) -> Self:
        """
        Sets the callback for this modal.

        Parameters
        ----------
        callback : :type:`ModalCallback`
            The callback to register for this modal.

        Raises
        ------
        `TypeError`
            The callback provided wasn't a coroutine function.
        """
        if not inspect.iscoroutinefunction(callback):
            raise TypeError("Component Callback methods must be couroutines.")

        self._callback = callback

        return self
