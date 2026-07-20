from collections.abc import Callable
from typing import TYPE_CHECKING

from mizuki.enums.components import ComponentType
from mizuki.payloads.components import ComponentPayload

if TYPE_CHECKING:
    from mizuki.objects.components import Component
    from mizuki.payloads.components import (
        BaseComponentPayload,
        BaseSelectPayload,
        ComponentTypeLiteral,
        SelectTypeLiteral,
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
