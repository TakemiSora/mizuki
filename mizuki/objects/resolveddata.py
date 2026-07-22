from typing import TYPE_CHECKING

from mizuki.objects.user import User
from mizuki.objects.member import PartialMember, ResolvedMember
from mizuki.objects.role import Role
from mizuki.objects.channel import parse_channel_payload
from mizuki.objects.message import PartialMessage, Attachment

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.payloads.interaction import ResolvedDataPayload

__all__ = ("ResolvedData",)


class ResolvedData:
    __slots__ = ("users", "members", "roles", "channels", "messages", "attachments")

    def __init__(
        self, data: ResolvedDataPayload, *, guild_id: int | None, state: ConnectionState
    ):
        self.users = {
            int(id): User(payload, state=state)
            for id, payload in data.get("users", {}).items()
        }

        self.members = (
            {
                int(id): ResolvedMember._from_partial_member(
                    PartialMember(
                        payload, guild_id=guild_id, user_id=int(id), state=state
                    ),
                    user=self.users[int(id)],
                )
                for id, payload in data.get("members", {}).items()
            }
            if guild_id is not None
            else {}
        )

        self.roles = {
            int(id): Role(payload) for id, payload in data.get("roles", {}).items()
        }

        self.channels = {
            int(id): parse_channel_payload(payload, partial=True, state=state)
            for id, payload in data.get("channels", {}).items()
        }

        self.messages = {
            int(id): PartialMessage(payload, state=state)
            for id, payload in data.get("messages", {}).items()
        }

        self.attachments = {
            int(id): Attachment(payload, state=state)
            for id, payload in data.get("attachments", {}).items()
        }
