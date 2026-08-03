from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Self

from mizuki._utils import _MISSING, JSONPayload, assign_val, assign_val_dict, scls
from mizuki.enums.channel import ChannelType
from mizuki.enums.components import DefaultSelectValueType
from mizuki.objects.channel import PartialGuildChannel, PartialThreadChannel
from mizuki.objects.components.common import BaseComponentResponse, BaseSelect
from mizuki.objects.member import ResolvedMember
from mizuki.objects.message import Attachment, PartialMessage
from mizuki.objects.role import Role
from mizuki.objects.resolveddata import ResolvedData
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.user import User
from mizuki.public_utils import generate_custom_id

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.payloads.components import (
        ChannelSelectPayload,
        DefaultSelectValuePayload,
        ObjectSelectPayload,
        ObjectSelectResponsePayload,
        ObjectSelectTypeLiteral,
    )

__all__ = (
    "DefaultSelectValue",
    "UserSelectResponse",
    "UserSelect",
    "RoleSelectResponse",
    "RoleSelect",
    "MentionableSelectResponse",
    "MentionableSelect",
    "ChannelSelectResponse",
    "ChannelSelect",
)


class DefaultSelectValue:
    __slots__ = ("id", "type")

    id: Snowflake
    "The ID of the object."

    type: DefaultSelectValueType
    "The type of object the ID refers to."

    def __init__(self, data: DefaultSelectValuePayload):
        self.id = Snowflake(data["id"])
        self.type = DefaultSelectValueType(data["type"])

    def _to_dict(self) -> JSONPayload:
        return {"id": self.id, "type": self.type.value}

    @classmethod
    def new(cls, id: int, *, type: DefaultSelectValueType) -> DefaultSelectValue:
        """
        Returns an instance of a DefaultSelectValue.

        Parameters
        ----------
        id : :class:`int`
            The ID of the target object.

        type : :class:`DefaultSelectValue`
            The type of object the ID refers to.
        """
        return assign_val(cls.__new__(cls), id=Snowflake(id), type=type)


class ObjectSelectResponse[T: ObjectSelectTypeLiteral](BaseComponentResponse):
    __slots__ = ("resolved", "values")

    type ValidObjectTypes = (
        User
        | ResolvedMember
        | Role
        | PartialGuildChannel
        | PartialThreadChannel
        | PartialMessage
        | Attachment
    )

    resolved: ResolvedData
    "The resolved data for this response."

    values: list[ValidObjectTypes]
    "The list of IDs of objects selected."

    def __init__(
        self,
        data: ObjectSelectResponsePayload[T],
        *,
        resolved_data: ResolvedData | None = None,
        state: ConnectionState | None = None,
    ):
        super().__init__(data)

        resolved = (
            scls(ResolvedData, data.get("resolved"), state=state) or resolved_data
        )
        if not resolved:
            raise ValueError(f"Received malformed ObjectSelect response payload.")

        self.resolved = resolved
        self.values = self._resolved_parser(data["values"], resolved_data=self.resolved)

    def _resolved_parser(
        self, ids: list[str], *, resolved_data: ResolvedData
    ) -> list[ValidObjectTypes]:
        raise NotImplementedError()


class ObjectSelect[
    T: ObjectSelectTypeLiteral,
    DefaultOptionParam: int | DefaultSelectValue,
    CallbackResponse: ObjectSelectResponse[ObjectSelectTypeLiteral],
](BaseSelect[CallbackResponse]):
    __slots__ = ("default_values",)

    default_values: list[DefaultSelectValue]
    "The default values selected in the select component."

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
        custom_id: str = _MISSING,
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
        custom_id : :class:`str`, optional
            The custom ID of the Select. Auto-generated if not provided.

        id : :class:`int`, optional
            Optional Unique identifier for the Select.

        placeholder : :class:`str`, optional
            The placeholder string shown on the Select.

        min_values : :class:`int`, optional
            The minimum amount of values the user has to select.

        max_values : :class:`int`, optional
            The maximum amount of values the user can select.

        default_values : list[:class:`int` | :class:`DefaultSelectValue`]
            The options that are selected by default on this select. You must provide DefaultSelectValue for MentionableSelect.

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
                        "Cannot auto convert integer IDs to DefaultSelectValue in MentionableSelect."
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
                        "custom_id": custom_id or generate_custom_id(),
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


class UserSelectResponse(ObjectSelectResponse[Literal[5]]):
    """
    Represents a response from an UserSelect component.
    """

    values: list[User]
    "The list of users that were selected in this component."

    def _resolved_parser(
        self, ids: list[str], *, resolved_data: ResolvedData
    ) -> list[User]:
        return [resolved_data.users[int(id)] for id in ids]


class UserSelect(
    ObjectSelect[Literal[5], int | DefaultSelectValue, UserSelectResponse]
):
    """
    Represents an UserSelect component.
    """

    _TYPE = 5
    _DEFAULT_OPTION_TYPE = DefaultSelectValueType.USER


class RoleSelectResponse(ObjectSelectResponse[Literal[6]]):
    """
    Represents a response from a RoleSelect component.
    """

    values: list[Role]
    "The list of roles that were selected in this component."

    def _resolved_parser(
        self, ids: list[str], *, resolved_data: ResolvedData
    ) -> list[Role]:
        return [resolved_data.roles[int(id)] for id in ids]


class RoleSelect(
    ObjectSelect[Literal[6], int | DefaultSelectValue, RoleSelectResponse]
):
    """
    Represents a RoleSelect component.
    """

    _TYPE = 6
    _DEFAULT_OPTION_TYPE = DefaultSelectValueType.ROLE


class MentionableSelectResponse(ObjectSelectResponse[Literal[7]]):
    """
    Represents a response from a MentionableSelect component.
    """

    type Mentionable = (
        User | Role | PartialGuildChannel | PartialThreadChannel | ResolvedMember
    )

    values: list[Mentionable]
    "The list of mentionables that were selected in this component."

    def _resolved_parser(
        self, ids: list[str], *, resolved_data: ResolvedData
    ) -> list[Mentionable]:
        return [resolved_data.get_mentionable(int(id)) for id in ids]


class MentionableSelect(
    ObjectSelect[Literal[7], DefaultSelectValue, MentionableSelectResponse]
):
    """
    Represents a MentionableSelect component.
    """

    _TYPE = 7
    _DEFAULT_OPTION_TYPE = None


class ChannelSelectResponse(ObjectSelectResponse[Literal[8]]):
    """
    Represents a response from a ChannelSelect component.
    """

    values: list[PartialGuildChannel | PartialThreadChannel]
    "The list of channels that were selected in this component."

    def _resolved_parser(
        self, ids: list[str], *, resolved_data: ResolvedData
    ) -> list[PartialGuildChannel | PartialThreadChannel]:
        return [resolved_data.channels[int(id)] for id in ids]


class ChannelSelect(
    ObjectSelect[Literal[8], int | DefaultSelectValue, ChannelSelectResponse]
):
    """
    Represents a ChannelSelect component.
    """

    __slots__ = ("channel_types",)

    channel_types: list[ChannelType]
    "The list of type of channels that can be selected in this component."

    def __init__(self, data: ChannelSelectPayload):
        super().__init__(data)

        self.channel_types = [ChannelType(d) for d in data.get("channel_types", [])]

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
            channel_types=[t.value for t in self.channel_types],
            required=self.required if self.required is not True else None,
            disabled=self.disabled or None,
        )

    @classmethod
    def new(
        cls,
        *,
        custom_id: str = _MISSING,
        id: int = _MISSING,
        placeholder: str = _MISSING,
        min_values: int = _MISSING,
        max_values: int = _MISSING,
        default_values: list[int | DefaultSelectValue] = _MISSING,
        channel_types: list[ChannelType] = _MISSING,
        required: bool = True,
        disabled: bool = False,
    ) -> ChannelSelect:
        """
        Creates a new Select instance.

        Parameters
        ----------
        custom_id : :class:`str`, optional
            The custom ID of the Select. Auto-generated if not provided.

        id : :class:`int`, optional
            Optional Unique identifier for the Select.

        placeholder : :class:`str`, optional
            The placeholder string shown on the Select.

        min_values : :class:`int`, optional
            The minimum amount of values the user has to select.

        max_values : :class:`int`, optional
            The maximum amount of values the user can select.

        default_values : list[:class:`int` | :class:`DefaultSelectValue`]
            The options that are selected by default on this select.

        channel_types : list[:class:`ChannelType`]
            The list of channel types that can be selected in this select.

        required : :class:`bool`, optional
            Whether this Select is required in modals.

        disabled : :class:`bool`, optional
            Whether this Select is disabled in messages.
        """
        return assign_val(
            cls({"type": 8, "custom_id": custom_id or generate_custom_id()}),
            id=id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            default_values=(
                [
                    DefaultSelectValue.new(i, type=DefaultSelectValueType.CHANNEL)
                    if isinstance(i, int)
                    else i
                    for i in default_values
                ]
                if default_values
                else []
            ),
            channel_types=channel_types,
            required=required,
            disabled=disabled,
        )
