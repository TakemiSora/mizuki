import inspect
from typing import overload, Literal

from mizuki.enums.channel import ChannelType
from mizuki.enums.command import CommandOptionType
from mizuki.objects.command import (
    ApplicationCommandChoice,
    ApplicationCommandOption,
    Localization,
)
from mizuki._utils import CoroDecorator, CoroFunc, _MISSING, assign_val

__all__ = ("Parameter", "parameters")


class Parameter:
    __slots__ = (
        "type",
        "name",
        "name_localizations",
        "description",
        "description_localizations",
        "required",
        "choices",
        "channel_types",
        "min_value",
        "max_value",
        "min_length",
        "max_length",
        "autocomplete",
    )

    @overload
    def __init__(
        self,
        *,
        type: Literal[CommandOptionType.STRING] = _MISSING,
        name: str = _MISSING,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        required: bool = _MISSING,
        choices: list[ApplicationCommandChoice] = _MISSING,
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        type: Literal[CommandOptionType.INTEGER] = _MISSING,
        name: str = _MISSING,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        required: bool = _MISSING,
        choices: list[ApplicationCommandChoice] = _MISSING,
        min_value: int = _MISSING,
        max_value: int = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        type: Literal[
            CommandOptionType.BOOLEAN,
            CommandOptionType.USER,
            CommandOptionType.ROLE,
            CommandOptionType.MENTIONABLE,
            CommandOptionType.ATTACHMENT,
        ] = _MISSING,
        name: str = _MISSING,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        required: bool = _MISSING,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        type: Literal[CommandOptionType.CHANNEL] = _MISSING,
        name: str = _MISSING,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        required: bool = _MISSING,
        channel_types: list[ChannelType] = _MISSING,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        type: Literal[CommandOptionType.NUMBER] = _MISSING,
        name: str = _MISSING,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        required: bool = _MISSING,
        choices: list[ApplicationCommandChoice] = _MISSING,
        min_value: float = _MISSING,
        max_value: float = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> None: ...

    def __init__(
        self,
        *,
        type: CommandOptionType = _MISSING,
        name: str = _MISSING,
        name_localizations: Localization = _MISSING,
        description: str = "...",
        description_localizations: Localization = _MISSING,
        required: bool = _MISSING,
        choices: list[ApplicationCommandChoice] = _MISSING,
        channel_types: list[ChannelType] = _MISSING,
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        min_value: int | float = _MISSING,
        max_value: int | float = _MISSING,
        autocomplete: bool = _MISSING,
    ):
        self.type = type
        self.name = name
        self.name_localizations = name_localizations
        self.description = description
        self.description_localizations = description_localizations
        self.required = required
        self.choices = choices
        self.channel_types = channel_types
        self.min_length = min_length
        self.max_length = max_length
        self.min_value = min_value
        self.max_value = max_value
        self.autocomplete = autocomplete


def parameters(**parameters: Parameter) -> CoroDecorator:
    def decorator(func: CoroFunc) -> CoroFunc:
        func_parameters = list(inspect.signature(func).parameters.values())
        options: dict[str, ApplicationCommandOption] = {}

        for param in func_parameters[1:]:
            if param.annotation is inspect.Parameter.empty:
                raise ValueError(
                    f"No type hint for slash command function={func.__name__}: '{param.name}'"
                )

            options[param.name] = assign_val(
                ApplicationCommandOption._from_function_param(param),
                **(
                    {k: getattr(deco_parameter, k) for k in deco_parameter.__slots__}
                    if (deco_parameter := parameters.get(param.name)) is not None
                    else {}
                ),
            )

        setattr(func, "__command_options__", options)
        return func

    return decorator
