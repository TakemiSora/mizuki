from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from mizuki._utils import _MISSING, JSONPayload, assign_val_dict, scls
from mizuki.flags import RoleFlags
from mizuki.objects.asset import Asset
from mizuki.objects.permissions import Permissions
from mizuki.objects.snowflake import Snowflake
from mizuki.payloads.role import (
    PartialRolePayload,
    RoleColorsPayload,
    RolePayload,
    RoleTagsPayload,
)

if TYPE_CHECKING:
    from mizuki.file import File
    from mizuki.objects import Member
    from mizuki.state import ConnectionState

__all__ = ("PartialRole", "Role", "RoleColors", "RolePositionChange", "RoleTags")


class RoleColors:
    """Represents the colors of a role."""

    __slots__ = ("primary", "secondary", "tertiary")

    primary: int
    "The primary color."

    secondary: int | None
    "The secondary color."

    tertiary: int | None
    "The tertiary color."

    def __init__(self, data: RoleColorsPayload):
        self.primary = data["primary_color"]
        self.secondary = data["secondary_color"]
        self.tertiary = data["tertiary_color"]

    @classmethod
    def new(
        cls, primary: int, secondary: int | None = None, tertiary: int | None = None
    ) -> RoleColors:
        """Returns an instance of the created RoleColors object.

        Parameters
        ----------
        primary : :class:`int`
            The primary color of the role.

        secondary : :class:`int` | :obj:`None`, optional
            The secondary color of the role.

        tertiary : :class:`int` | :obj:`None`, optional
            The teritary color of the role.
        """
        return cls(
            {
                "primary_color": primary,
                "secondary_color": secondary,
                "tertiary_color": tertiary,
            }
        )

    def _to_dict(self) -> JSONPayload:
        return {
            "primary_color": self.primary,
            "secondary_color": self.secondary,
            "tertiary_color": self.tertiary,
        }


class RoleTags:
    """The tags of a role."""

    __slots__ = (
        "available_for_purchase",
        "bot_id",
        "guild_connections",
        "integration_id",
        "premium_subscriber",
        "subscription_listing_id",
    )

    bot_id: Snowflake | None
    "The ID of the bot this role belongs to."

    integration_id: Snowflake | None
    "The ID of the integration this role belongs to."

    premium_subscriber: bool
    "Whether this role is the guild's booster role."

    subscription_listing_id: Snowflake | None
    "The ID of this role's subscription sku."

    available_for_purchase: bool
    "Whether this role is available for purchase."

    guild_connections: bool
    "Whether this role is a guild's linked role."

    def __init__(self, data: RoleTagsPayload):
        self.bot_id = Snowflake._from_str(data.get("bot_id"))
        self.integration_id = Snowflake._from_str(data.get("integration_id"))
        self.premium_subscriber = "premium_subscriber" in data
        self.subscription_listing_id = Snowflake._from_str(
            data.get("subscription_listing_id")
        )
        self.available_for_purchase = "available_for_purchase" in data
        self.guild_connections = "guild_connections" in data


class PartialRole:
    """Represents partial data about a role."""

    __slots__ = (
        "_guild_id",
        "_state",
        "colors",
        "icon",
        "id",
        "name",
        "position",
        "unicode_emoji",
    )

    id: Snowflake
    "The ID of the role."

    name: str
    "The name of the role."

    colors: RoleColors
    "The colors of the role."

    icon: Asset | None
    "The icon of the role if any."

    unicode_emoji: str | None
    "The unicode emoji related to this role."

    position: int
    "The position of this role in the guild."

    def __init__(
        self, data: PartialRolePayload, *, guild_id: int, state: ConnectionState
    ):
        self._state = state
        self._guild_id = guild_id
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.colors = RoleColors(data["colors"])
        self.icon = Asset._from_role_icon(self.id, data.get("icon"))
        self.unicode_emoji = data.get("unicode_emoji")
        self.position = data["position"]

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented

    def __hash__(self) -> int:
        return self.id

    @property
    def created_at(self) -> datetime:
        return self.id.created_at


class Role(PartialRole):
    """Represents a discord role."""

    __slots__ = ("flags", "hoist", "managed", "mentionable", "permissions", "tags")

    hoist: bool
    "Whether this role is hoisted separately from others."

    permissions: Permissions
    "The permissions this role has."

    managed: bool
    "Whether this role is managed by an integration."

    mentionable: bool
    "Whether this role is mentionable by anyone."

    tags: RoleTags | None
    "The tags of this role."

    flags: RoleFlags
    "The flags of this role."

    def __init__(self, data: RolePayload, *, guild_id: int, state: ConnectionState):
        super().__init__(data, guild_id=guild_id, state=state)
        self.hoist = data["hoist"]
        self.permissions = Permissions(int(data["permissions"]))
        self.managed = data["managed"]
        self.mentionable = data["mentionable"]
        self.tags = scls(RoleTags, data.get("tags"))
        self.flags = RoleFlags(data["flags"])

    async def add(
        self,
        user_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> Member:
        """Add a role to a member.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target member.

        audit_log_reason : :class:`str`, optional
            The reason to show in audit log for this change.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild, user or role.

        :class:`Forbidden`
            You are forbidden from editing roles or adding that role.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.add_role(
            self._guild_id, user_id, self.id, audit_log_reason=audit_log_reason
        )

    async def remove(
        self,
        user_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> None:
        """Removes a role from a member.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target member.

        audit_log_reason : :class:`str`, optional
            The reason to show in audit log for this change.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild, user or role.

        :class:`Forbidden`
            You are forbidden from editing roles or removing that role.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.remove_role(
            self._guild_id, user_id, self.id, audit_log_reason=audit_log_reason
        )

    async def edit(
        self,
        *,
        name: str | None = _MISSING,
        permissions: Permissions | None = _MISSING,
        colors: RoleColors | None = _MISSING,
        hoist: bool | None = _MISSING,
        icon: File | str | None = _MISSING,
        unicode_emoji: str | None = _MISSING,
        mentionable: bool | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Role:
        """Edit a role in a guild.

        .. note::

            All parameters are optional.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the target guild.

        role_id : :class:`int`
            The ID of the target role.

        name : :class:`int`
            The name of the role.

        permissions : :class:`~mizuki.Permissions`
            The permissions for the role.

        colors : :class:`~mizuki.RoleColors`
            The colors for the role.

        hoist : :class:`bool`
            Whether the role is hoisted/shown separately in member lists.

        icon : :class:`~mizuki.File` | :class:`str` | :obj:`None`
            The icon of the role.

        unicode_emoji : :class:`str` | :obj:`None`
            The related unicode emoji for new role.

        mentionable : :class:`bool`
            Whether the role is mentionable.

        audit_log_reason : :class:`str`
            The reason to show in the audit log for the editing of this role.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to edit roles in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.edit_role(
            self._guild_id,
            self.id,
            **{k: v for k, v in locals().items() if k != "self"},
        )

    async def delete(self, *, audit_log_reason: str = _MISSING) -> None:
        """Delete a role in a guild.

        Parameters
        ----------
        audit_log_reason : :class:`str`
            The reason to show in the audit log for the editing of this role.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to delete that role in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.delete_role(
            self._guild_id, self.id, audit_log_reason=audit_log_reason
        )


@dataclass(slots=True)
class RolePositionChange:
    """Used to specify which role positions to change in :meth:`~mizuki.Guild.edit_role_positions`"""

    id: int
    "The ID of the role."

    position: int | None = _MISSING
    "The position to change it to."

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict({"id": self.id}, _MISSING, position=self.position)
