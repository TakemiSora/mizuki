from __future__ import annotations
from typing import cast

from ..enums.command import ApplicationCommandType, CommandOptionType
from ..enums.interaction import (
    ApplicationIntegrationType,
    InteractionCallbackType,
    InteractionContextType,
    InteractionType,
)
from ..errors import UnknownInteractionType
from ..http import HTTPClient, Path
from ..payloads.interaction import (
    ApplicationCommandInteractionOptionPayload,
    InteractionCallbackDataPayload,
    InteractionData,
    InteractionPayload,
    InteractionResponseCallbackPayload,
    InvokedApplicationCommandPayload,
    ResolvedDataPayload,
)
from ..utils import scls, sint
from .channel import parse_channel_payload
from .guild import Guild
from .member import Member, PartialMember
from .message import Attachment, Message, PartialMessage
from .permissions import Permissions
from .role import Role
from .snowflake import Snowflake
from .user import User

__all__ = (
    "Interaction",
)

class ResolvedData:
    __slots__ = (
        "users",
        "members",
        "roles",
        "channels",
        "messages",
        "attachments"
    )

    def __init__(self, data: ResolvedDataPayload, *, guild_id: int | None):
        self.users = {Snowflake(id): User(payload) for id, payload in data.get("users", {}).items()}
        self.members = {Snowflake(id): PartialMember(payload, guild_id=guild_id, user_id=int(id)) for id, payload in data.get("members", {}).items()} if guild_id is not None else {}
        self.roles = {Snowflake(id): Role(payload) for id, payload in data.get("roles", {}).items()}
        self.channels = {Snowflake(id): parse_channel_payload(payload, partial=True) for id, payload in data.get("channels", {}).items()}
        self.messages = {Snowflake(id): PartialMessage(payload) for id, payload in data.get("messages", {}).items()}
        self.attachments = {Snowflake(id): Attachment(payload) for id, payload in data.get("attachments", {}).items()}
        
class InvokedApplicationCommandOption:
    __slots__ = (
        "name",
        "type",
        "value",
        "options",
        "focused"
    )
    
    def __init__(self, data: ApplicationCommandInteractionOptionPayload):
        self.name = data["name"]
        self.type = CommandOptionType(data["type"])
        self.value = data.get("value")
        self.options = [InvokedApplicationCommandOption(o) for o in data.get("options", [])]
        self.focused = data.get("focused", False)
  
class InvokedApplicationCommand:
    __slots__ = (
        "id",
        "name",
        "type",
        "resolved",
        "options",
        "guild_id",
        "target_id"
    )

    def __init__(self, data: InvokedApplicationCommandPayload):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.type = ApplicationCommandType(data["type"])
        self.options = [InvokedApplicationCommandOption(o) for o in data.get("options", [])]
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.resolved = scls(ResolvedData, data.get("resolved"), guild_id=self.guild_id)
        self.target_id = Snowflake._from_str(data.get("target_id"))
        
def parse_interaction_data(type: InteractionType, data: InteractionData) -> InvokedApplicationCommand: #moretypes later
    match type:
        case (
            InteractionType.APPLICATION_COMMAND
            | InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE
        ):
            return InvokedApplicationCommand(cast(InvokedApplicationCommandPayload, data))
        case _:
            raise UnknownInteractionType(f"Recieved unknown interaction type '{type}'")
            
class ResponseHandler:
    __slots__ = (
        "_http",
        "interaction_id",
        "interaction_token"
    )
    
    def __init__(self, http: HTTPClient, interaction_id: int, interaction_token: str):
        self._http = http
        self.interaction_id = interaction_id
        self.interaction_token = interaction_token
        
    async def _post(self, type: InteractionCallbackType, data: InteractionCallbackDataPayload):
        await self._http.request(
            Path(
                "POST",
                "interactions/{interaction_id}/{interaction_token}/callback",
                interaction_id = self.interaction_id,
                interaction_token = self.interaction_token
            ),
            json = InteractionResponseCallbackPayload(
                type = type.value,
                data = data
            )
        )
        
    async def send_message(
        self,
        content: str | None = None
    ):
        if content:
            return await self._post(
                InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                InteractionCallbackDataPayload(
                    content = content
                )
            )
        raise ValueError("Missing 'content' field in responding to interaction.")

class Interaction:
    __slots__ = (
        "_http",
        "response",
        "id",
        "application_id",
        "type",
        "data",
        "guild",
        "guild_id",
        "channel",
        "channel_id",
        "member",
        "user",
        "token",
        "version",
        "message",
        "app_permissions",
        "locale",
        "guild_locale",
        "authorizing_integration_owners",
        "context",
        "attachment_size_limit"
    )

    def __init__(self, http: HTTPClient, data: InteractionPayload, *, guild: Guild | None = None):
        self._http = http
        self.id = Snowflake(data["id"])
        self.application_id = Snowflake(data["application_id"])
        self.type = InteractionType(data["type"])
        self.data = parse_interaction_data(self.type, i) if (i := data.get("data")) is not None else None
        self.guild = guild
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.channel = parse_channel_payload(c, partial=False) if (c := data.get("channel")) is not None else None
        self.channel_id = Snowflake._from_str(data.get("channel_id"))
        self.member = scls(Member, data.get("member"), guild_id=self.guild_id)
        self.user = scls(User, data.get("user"))
        self.token = data["token"]
        self.version = data["version"]
        self.message = scls(Message, data.get("message"))
        self.app_permissions = Permissions(int(data["app_permissions"]))
        self.locale = data.get("locale")
        self.guild_locale = data.get("guild_locale")
        self.authorizing_integration_owners = {ApplicationIntegrationType(int(a)): (Snowflake(id) if id != "0" else 0) for a, id in data.get("authorizing_integration_owners", {}).items()}
        self.context = scls(InteractionContextType, data.get("context"))
        self.attachment_size_limit = data["attachment_size_limit"]
        
        self.response = ResponseHandler(http, self.id, self.token)