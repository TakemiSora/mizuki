from typing import cast

from mizuki._utils import _MISSING, assign_val_dict, maybe_iter, mgetattr, mtd
from mizuki.file import File, maybe_encode_file
from mizuki.http import Path
from mizuki.managers._types import BaseManager
from mizuki.objects.member import Member
from mizuki.objects.permissions import Permissions
from mizuki.objects.role import Role, RoleColors, RolePositionChange
from mizuki.objects.snowflake import Snowflake
from mizuki.payloads.role import RolePayload


class RoleManager(BaseManager):
    """Manager used to fetch :class:`~mizuki.Role` objects."""

    async def add_member_role(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> Member:
        """Add a role to a member.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the guild the target member is in.

        user_id : :class:`int`
            The ID of the target member.

        role_id : :class:`int`
            The ID of the role to add.

        audit_log_reason : :class:`str`, optional
            The reason to show in audit log for this change.

        Parameters
        ----------
        :class:`NotFound`
            Could not find that guild, user or role.

        :class:`Forbidden`
            You are forbidden from editing roles or adding that role.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return Member(
            await self._state.http.request(
                Path(
                    "PUT",
                    "guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                    guild_id=guild_id,
                    user_id=user_id,
                    role_id=role_id,
                ),
                audit_log_reason=audit_log_reason,
            ),
            guild_id=guild_id,
            user_id=user_id,
            state=self._state,
        )

    async def remove_member_role(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> None:
        """Removes a role from a member.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the guild the target member is in.

        user_id : :class:`int`
            The ID of the target member.

        role_id : :class:`int`
            The ID of the role to remove.

        audit_log_reason : :class:`str`, optional
            The reason to show in audit log for this change.

        Parameters
        ----------
        :class:`NotFound`
            Could not find that guild, user or role.

        :class:`Forbidden`
            You are forbidden from editing roles or removing that role.

        :class:`HTTPException`
            A HTTP error occured.
        """
        await self._state.http.request(
            Path(
                "DELETE",
                "guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            audit_log_reason=audit_log_reason,
        )

    async def fetch_roles(self, guild_id: int) -> list[Role]:
        """Fetch all the roles of a guild.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the guild to fetch the roles of.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to fetch roles of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return [
            Role(r)
            for r in await self._state.http.request(
                Path("GET", "guilds/{guild_id}/roles", guild_id=guild_id),
            )
        ]

    async def fetch_role(self, guild_id: int, role_id: int) -> Role:
        """Fetch all the roles of a guild.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the target guild.

        role_id : :class:`int`
            The ID of the target role.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to fetch roles of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return Role(
            await self._state.http.request(
                Path(
                    "GET",
                    "guilds/{guild_id}/roles/{role_id}",
                    guild_id=guild_id,
                    role_id=role_id,
                ),
            )
        )

    async def fetch_role_member_counts(self, guild_id: int) -> dict[Snowflake, int]:
        """Fetch role count for every role in a guild.

        Returns a dictonary with role ID as keys and their member count as values.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the target guild.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to fetch roles of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return {
            Snowflake(k): v
            for k, v in (
                cast(
                    dict[str, int],
                    await self._state.http.request(
                        Path(
                            "GET",
                            "guilds/{guild_id}/roles/member-counts",
                            guild_id=guild_id,
                        )
                    ),
                )
            ).items()
        }

    async def create_role(
        self,
        guild_id: int,
        *,
        name: str = _MISSING,
        permissions: Permissions = _MISSING,
        colors: RoleColors = _MISSING,
        hoist: bool = _MISSING,
        icon: File | str | None = _MISSING,
        unicode_emoji: str | None = _MISSING,
        mentionable: bool = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Role:
        """Create a new role in a guild.

        All parameters besides ``guild_id`` are optional.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the target guild.

        name : :class:`int`
            The name of the new role, defaults to "new role".

        permissions : :class:`~mizuki.Permissions`
            The permissions for the new role.

        colors : :class:`~mizuki.RoleColors`
            The colors for the new role.

        hoist : :class:`bool`
            Whether the role is hoisted/shown separately in member lists.

        icon : :class:`~mizuki.File` | :class:`str` | :obj:`None`
            The icon of the new role.

        unicode_emoji : :class:`str` | :obj:`None`
            The related unicode emoji for the new role.

        mentionable : :class:`bool`
            Whether the role is mentionable.

        audit_log_reason : :class:`str`
            The reason to show in the audit log for the creation of this role.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to create roles in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return Role(
            await self._state.http.request(
                Path("POST", "guilds/{guild_id}/roles", guild_id=guild_id),
                json=assign_val_dict(
                    {},
                    _MISSING,
                    name=name,
                    permissions=mgetattr(permissions, "value"),
                    colors=mtd(colors),
                    hoist=hoist,
                    icon=await maybe_encode_file(icon),
                    unicode_emoji=unicode_emoji,
                    mentionable=mentionable,
                ),
                audit_log_reason=audit_log_reason,
            )
        )

    async def edit_role_positions(
        self,
        guild_id: int,
        *changes: RolePositionChange,
        audit_log_reason: str = _MISSING,
    ) -> list[Role]:
        """Edit role positions in a guild.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the target guild.

        *changes : :class:`~mizuki.RolePositionChange`
            The changes to be made to the role positions.

        audit_log_reason : :class:`str`, optional
            The reason to show in the audit log for this change.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to edit role positions in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return [
            Role(d)
            for d in cast(
                list[RolePayload],
                await self._state.http.request(
                    Path("PATCH", "guilds/{guild_id}/roles", guild_id=guild_id),
                    json=maybe_iter(changes),
                    audit_log_reason=audit_log_reason,
                ),
            )
        ]

    async def edit_role(
        self,
        guild_id: int,
        role_id: int,
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

            All parameters besides ``guild_id`` are optional.

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
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to edit roles in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return Role(
            cast(
                RolePayload,
                await self._state.http.request(
                    Path(
                        "PATCH",
                        "guilds/{guild_id}/roles/{role_id}",
                        guild_id=guild_id,
                        role_id=role_id,
                    ),
                    json=assign_val_dict(
                        {},
                        _MISSING,
                        name=name,
                        permissions=mgetattr(permissions, "value"),
                        colors=mtd(colors),
                        hoist=hoist,
                        icon=await maybe_encode_file(icon),
                        unicode_emoji=unicode_emoji,
                        mentionable=mentionable,
                    ),
                    audit_log_reason=audit_log_reason,
                ),
            )
        )

    async def delete_role(
        self, guild_id: int, role_id: int, *, audit_log_reason: str = _MISSING
    ) -> None:
        """Delete a role in a guild.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the target guild.

        role_id : :class:`int`
            The ID of the target role.

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
        await self._state.http.request(
            Path(
                "DELETE",
                "guilds/{guild_id}/roles/{role_id}",
                guild_id=guild_id,
                role_id=role_id,
            ),
            audit_log_reason=audit_log_reason,
        )
