from datetime import timedelta
import inspect
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, Self

from mizuki._utils import JSONPayload, _MISSING
from mizuki.enums.components import ComponentType

if TYPE_CHECKING:
    from mizuki.objects.components import Component
    from mizuki.objects.interaction import Interaction
    from mizuki.payloads.components import (
        BaseComponentPayload,
        BaseComponentResponsePayload,
        BaseSelectPayload,
        ComponentPayload,
        ComponentTypeLiteral,
        InteractiveComponentTypeLiteral,
        SelectTypeLiteral,
    )


class BaseComponentResponse:
    __slots__ = ("custom_id", "id", "component_type")

    custom_id: str
    "The custom ID of the component."

    id: int | None
    "Optional unique identifier for the component."

    component_type: ComponentType
    "The type of the component."

    def __init__[T: InteractiveComponentTypeLiteral](
        self, data: BaseComponentResponsePayload[T]
    ):
        self.custom_id = data["custom_id"]
        self.id = data.get("id")

        if (
            resolved_component_type := (data.get("component_type") or data.get("type"))
        ) is None:
            raise ValueError("Recieved malformed component response without a type.")

        self.component_type = ComponentType(resolved_component_type)


class HasCallbackResponse[CallbackResponse: BaseComponentResponse]:
    __slots__ = ()

    type ComponentCallback = Callable[
        [Interaction, CallbackResponse], Coroutine[Any, Any, Any]
    ]

    def set_callback(self, callback: ComponentCallback) -> Self:
        """
        Sets the callback for this component.

        ..note ::

            This method also returns the class instance to allow chaining.


        Parameters
        ----------
        callback : :type:`ComponentCallback`
            The callback to register for this component

        Raises
        ------
        `TypeError`
            The callback provided wasn't a coroutine function.
        """
        if not inspect.iscoroutinefunction(callback):
            raise TypeError("Component Callback methods must be couroutines.")

        self._callback = callback

        return self

    def set_timeout(self, timeout: timedelta | int | None) -> Self:
        """
        Sets the amount of the time the bot will keep track of this component to respond to it.

        .. note::

            This method also returns the class instance to allow chaining.


        Paramters
        ---------
        timeout : :class:`timedelta` | :class:`int` | :class:`None`
            The timeout to set for this component. Integers are treated as seconds. Use ``None`` to disable timeout.
        """
        if isinstance(timeout, int):
            timeout = timedelta(seconds=timeout)

        self._timeout = timeout
        return self


class BaseComponent:
    __slots__ = ("id", "type", "_timeout", "_callback")

    type: ComponentType
    "The type of the component."

    id: int | None
    "An optional identifier for the component."

    def __init__[T: ComponentTypeLiteral](self, data: BaseComponentPayload[T]):
        self.type = ComponentType(data["type"])
        self.id = data.get("id")

    def _to_dict(self) -> JSONPayload:
        raise NotImplementedError()


class BaseSelect[CallbackResponse: BaseComponentResponse](
    BaseComponent, HasCallbackResponse[CallbackResponse]
):
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


def component_parser_gen[ReturnType: Component](
    component_map: dict[ComponentType, type[ReturnType]], item: str
) -> Callable[[ComponentPayload], ReturnType]:
    def parser(data: ComponentPayload) -> ReturnType:
        component_type = ComponentType(data["type"])

        try:
            return component_map[component_type](data)  # type: ignore # This is resolved correctly.
        except KeyError:
            raise ValueError(
                f"Component of type {component_type.value} cannot be inserted into {item}."
            )

    return parser
