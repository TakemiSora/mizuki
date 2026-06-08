from __future__ import annotations
from typing import cast, Any, Literal

from ..enums.command import ApplicationCommandType, CommandOptionType
from ..enums.interaction import (
    ApplicationIntegrationType,
    InteractionCallbackType,
    InteractionContextType,
    InteractionType,
)
from ..errors import (
    UnknownInteractionType,
    InteractionNotResponded,
    InteractionResponded
)
from ..http import HTTPClient, Path
from ..payloads.interaction import (
    ApplicationCommandInteractionOptionPayload,
    InteractionCallbackDataPayload,
    InteractionWebhookMessagePayload,
    InteractionData,
    InteractionPayload,
    InteractionResponseCallbackPayload,
    InvokedApplicationCommandPayload,
    ResolvedDataPayload,
)
from ..flags import MessageFlags
from .._utils import scls, _MISSING
from .channel import parse_channel_payload
from .embed import Embed
from .guild import Guild
from .member import Member, PartialMember, ResolvedMember
from .message import Attachment, Message, PartialMessage, AllowedMentions
from .permissions import Permissions
from .role import Role
from .snowflake import Snowflake
from .user import User

__all__ = (
    "ResolvedData",
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
        self.users = {
            int(id): User(payload)
            for id, payload in data.get("users", {}).items()
        }

        self.members = {
            int(id): ResolvedMember._from_partial_member(
                PartialMember(payload, guild_id=guild_id, user_id=int(id)),
                user=self.users[int(id)]
            )
            for id, payload in data.get("members", {}).items()
        } if guild_id is not None else {}

        self.roles = {
            int(id): Role(payload)
            for id, payload in data.get("roles", {}).items()
        }

        self.channels = {
            int(id): parse_channel_payload(payload, partial=True)
            for id, payload in data.get("channels", {}).items()
        }

        self.messages = {
            int(id): PartialMessage(payload)
            for id, payload in data.get("messages", {}).items()
        }

        self.attachments = {
            int(id): Attachment(payload)
            for id, payload in data.get("attachments", {}).items()
        }
        
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
            raise UnknownInteractionType(f"Received unknown interaction type '{type}'")
            
class ResponseHandler:
    __slots__ = (
        "_http",
        "interaction_id",
        "interaction_token",
        "application_id",
        "acknowledged"
    )
    
    def __init__(
        self,
        http: HTTPClient,
        interaction_id: int,
        interaction_token: str,
        application_id: Snowflake
    ):
        self._http = http
        self.interaction_id = interaction_id
        self.interaction_token = interaction_token
        self.application_id = application_id
        self.acknowledged = False
        
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

    async def send_response(
        self,
        content: str | None = None,
        *, tts: bool = False,
        embeds: list[Embed] | None = None,
        allowed_mentions: AllowedMentions = AllowedMentions.new(),
        flags: MessageFlags = MessageFlags(0),
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        suppress_notifications: bool = False,
        is_components_v2: bool = False,
        is_voice_message: bool = False
    ):
        if self.acknowledged:
            raise InteractionResponded()
        
        if any((content, embeds)):
            data = InteractionCallbackDataPayload(
                tts=tts,
                allowed_mentions=allowed_mentions._to_dict()
            )

            if content is not None: data["content"] = content
            if embeds is not None: data["embeds"] = [e._to_dict() for e in embeds]
            
            if ephemeral: flags |= MessageFlags.EPHEMERAL
            if suppress_embeds: flags |= MessageFlags.SUPPRESS_EMBEDS
            if suppress_notifications: flags |= MessageFlags.SUPPRESS_NOTIFICATIONS
            if is_components_v2: flags |= MessageFlags.IS_COMPONENTS_V2
            if is_voice_message: flags |= MessageFlags.IS_VOICE_MESSAGE
            if flags != 0: data["flags"] = flags
            
            await self._post(
                InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                data
            )
            self.acknowledged = True
            return
        
        raise ValueError("No sendable field was passed to the response")
    
    async def defer(
        self, *,
        ephemeral: bool = False
    ):
        if self.acknowledged:
            raise InteractionResponded()
        
        await self._post(
            InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
            InteractionCallbackDataPayload(
                flags = MessageFlags(MessageFlags.EPHEMERAL if ephemeral else 0)
            )
        )
        self.acknowledged = True

    async def send_followup(
        self,
        content: str | None = None,
        *, tts: bool = False,
        embeds: list[Embed] | None = None,
        allowed_mentions: AllowedMentions = AllowedMentions.new(),
        flags: MessageFlags = MessageFlags(0),
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        suppress_notifications: bool = False,
        is_components_v2: bool = False,
    ) -> Message:
        if not self.acknowledged:
            raise InteractionNotResponded()
        
        if any((content, embeds)):
            data = InteractionWebhookMessagePayload(
                tts=tts,
                allowed_mentions=allowed_mentions._to_dict()
            )

            if content is not None: data["content"] = content
            if embeds is not None: data["embeds"] = [e._to_dict() for e in embeds]

            if ephemeral: flags |= MessageFlags.EPHEMERAL
            if suppress_embeds: flags |= MessageFlags.SUPPRESS_EMBEDS
            if suppress_notifications: flags |= MessageFlags.SUPPRESS_NOTIFICATIONS
            if is_components_v2: flags |= MessageFlags.IS_COMPONENTS_V2
            if flags != 0: data["flags"] = flags.value

            return Message(await self._http.request(
                Path(
                    "POST",
                    "webhooks/{webhook_id}/{webhook_token}",
                    webhook_id = self.application_id,
                    webhook_token = self.interaction_token
                ),
                json = data
            ))
        
        raise ValueError("No sendable field was passed to the response")

    async def _webhook_messages_request(
        self, *,
        method: str,
        message: int | str = "@original",
        **kwargs: Any
    ) -> Any:
        return await self._http.request(
            Path(
                method,
                "webhooks/{webhook_id}/{webhook_token}/messages/{message}",
                webhook_id = self.application_id,
                webhook_token = self.interaction_token,
                message = str(message)
            ),
            **kwargs
        )

    async def fetch_original_response(self) -> Message:
        return Message(await self._webhook_messages_request(method="GET"))
    
    async def edit_original_response(
        self,
        content: str | None = _MISSING,
        *, embeds: list[Embed] | None = _MISSING,
        flags: MessageFlags = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        suppress_embeds: bool = _MISSING,
        is_components_v2: Literal[True] = _MISSING
    ) -> Message:
        if all(
            x is _MISSING
            for x in [
                content,
                embeds,
                flags,
                allowed_mentions,
                suppress_embeds,
                is_components_v2
            ]
        ):
            raise ValueError("No editable fields were passed in editing response.")
        
        data = InteractionWebhookMessagePayload()

        if content is not _MISSING: data["content"] = content
        if embeds is not _MISSING: data["embeds"] = [e._to_dict() for e in embeds] if embeds is not None else None
        if allowed_mentions is not _MISSING: data["allowed_mentions"] = allowed_mentions._to_dict() if allowed_mentions is not None else None
        if suppress_embeds is not _MISSING or is_components_v2 is not _MISSING:
            flags = MessageFlags(0)
            if suppress_embeds: flags |= MessageFlags.SUPPRESS_EMBEDS
            if is_components_v2: flags |= MessageFlags.IS_COMPONENTS_V2
            data["flags"] = flags
            
        return Message(await self._webhook_messages_request(
            method="PATCH",
            json=data
        ))

    async def delete_original_response(self):
        await self._webhook_messages_request(method="DELETE")

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
        self.channel = parse_channel_payload(c, partial=True) if (c := data.get("channel")) is not None else None
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
        
        self.response = ResponseHandler(http, self.id, self.token, self.application_id)