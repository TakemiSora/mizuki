from __future__ import annotations
from typing import Any, Literal, cast, TYPE_CHECKING

from mizuki._utils import _MISSING, assign_val_dict, mtd, scls
from mizuki.enums.command import ApplicationCommandType, CommandOptionType
from mizuki.enums.interaction import (
    ApplicationIntegrationType,
    InteractionCallbackType,
    InteractionContextType,
    InteractionType,
)
from mizuki.errors import (
    InteractionNotResponded,
    InteractionResponded,
    UnknownInteractionType,
)
from mizuki.file import File
from mizuki.flags import MessageFlags
from mizuki.http import Path
from mizuki.objects.channel import parse_channel_payload
from mizuki.objects.components.resp_parser import parse_component_response
from mizuki.objects.embed import Embed
from mizuki.objects.guild import Guild
from mizuki.objects.member import Member
from mizuki.objects.message import AllowedMentions, Message
from mizuki.objects.permissions import Permissions
from mizuki.objects.resolveddata import ResolvedData
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.user import User
from mizuki.payloads.interaction import (
    ApplicationCommandInteractionOptionPayload,
    InteractionCallbackDataPayload,
    InteractionDataPayload,
    InteractionPayload,
    InteractionResponseCallbackPayload,
    InteractionWebhookMessagePayload,
    InvokedApplicationCommandPayload,
)

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.objects.components import Component, ComponentResponse

__all__ = (
    "ResponseHandler",
    "Interaction",
)


class InvokedApplicationCommandOption:
    __slots__ = ("name", "type", "value", "options", "focused")

    def __init__(self, data: ApplicationCommandInteractionOptionPayload):
        self.name = data["name"]
        self.type = CommandOptionType(data["type"])
        self.value = data.get("value")
        self.options = [
            InvokedApplicationCommandOption(o) for o in data.get("options", [])
        ]
        self.focused = data.get("focused", False)


class InvokedApplicationCommand:
    __slots__ = ("id", "name", "type", "resolved", "options", "guild_id", "target_id")

    def __init__(
        self, data: InvokedApplicationCommandPayload, *, state: ConnectionState
    ):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.type = ApplicationCommandType(data["type"])
        self.options = [
            InvokedApplicationCommandOption(o) for o in data.get("options", [])
        ]
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.resolved = scls(
            ResolvedData, data.get("resolved"), guild_id=self.guild_id, state=state
        )
        self.target_id = Snowflake._from_str(data.get("target_id"))


def parse_interaction_data(
    type: InteractionType,
    data: InteractionDataPayload,
    *,
    guild_id: int | None,
    state: ConnectionState,
) -> InvokedApplicationCommand | ComponentResponse:
    match type:
        case (
            InteractionType.APPLICATION_COMMAND
            | InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE
        ):
            return InvokedApplicationCommand(
                cast(InvokedApplicationCommandPayload, data), state=state
            )
        case InteractionType.MESSAGE_COMPONENT:
            return parse_component_response(data, guild_id=guild_id, state=state)  # type: ignore # This is resolved.
        case _:
            raise UnknownInteractionType(f"Received unknown interaction type '{type}'")


class ResponseHandler:
    __slots__ = (
        "_state",
        "interaction_id",
        "interaction_token",
        "application_id",
        "acknowledged",
    )

    def __init__(
        self,
        interaction_id: int,
        interaction_token: str,
        application_id: Snowflake,
        *,
        state: ConnectionState,
    ):
        self._state = state
        self.interaction_id = interaction_id
        self.interaction_token = interaction_token
        self.application_id = application_id
        self.acknowledged = False

    async def _post(
        self,
        type: InteractionCallbackType,
        data: InteractionCallbackDataPayload,
        files: list[File] = _MISSING,
        components: list[Component] = _MISSING,
    ):
        await self._state.http.request(
            Path(
                "POST",
                "interactions/{interaction_id}/{interaction_token}/callback",
                interaction_id=self.interaction_id,
                interaction_token=self.interaction_token,
            ),
            json=InteractionResponseCallbackPayload(type=type.value, data=data),
            files=files,
            components=components,
        )

    async def send_response(
        self,
        content: str = _MISSING,
        *,
        tts: bool = False,
        embeds: list[Embed] = _MISSING,
        allowed_mentions: AllowedMentions = AllowedMentions.new(),
        files: list[File] = _MISSING,
        components: list[Component] = _MISSING,
        flags: MessageFlags = MessageFlags(0),
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        suppress_notifications: bool = False,
        is_components_v2: bool = False,
        is_voice_message: bool = False,
    ):
        if self.acknowledged:
            raise InteractionResponded()

        if any((content, embeds, files, components)):
            if ephemeral:
                flags |= MessageFlags.EPHEMERAL
            if suppress_embeds:
                flags |= MessageFlags.SUPPRESS_EMBEDS
            if suppress_notifications:
                flags |= MessageFlags.SUPPRESS_NOTIFICATIONS
            if is_components_v2:
                flags |= MessageFlags.IS_COMPONENTS_V2
            if is_voice_message:
                flags |= MessageFlags.IS_VOICE_MESSAGE

            await self._post(
                type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                files=files,
                data=assign_val_dict(
                    InteractionCallbackDataPayload(
                        tts=tts,
                        allowed_mentions=allowed_mentions._to_dict(),
                    ),
                    _MISSING,
                    content=content,
                    embeds=(
                        [embed._to_dict() for embed in embeds]
                        if embeds is not _MISSING
                        else _MISSING
                    ),
                    attachments=(
                        [file._to_attachment_dict(i) for i, file in enumerate(files)]
                        if files is not _MISSING
                        else _MISSING
                    ),
                    flags=flags.value,
                    components=(
                        [component._to_dict() for component in components]
                        if components is not _MISSING
                        else _MISSING
                    ),
                ),
                components=components,
            )
            self.acknowledged = True
            return

        raise ValueError("No sendable field was passed to the response")

    async def defer(self, *, ephemeral: bool = False):
        if self.acknowledged:
            raise InteractionResponded()

        await self._post(
            InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
            InteractionCallbackDataPayload(
                flags=MessageFlags(MessageFlags.EPHEMERAL if ephemeral else 0)
            ),
        )
        self.acknowledged = True

    async def send_followup(
        self,
        content: str = _MISSING,
        *,
        tts: bool = False,
        embeds: list[Embed] = _MISSING,
        allowed_mentions: AllowedMentions = AllowedMentions.new(),
        files: list[File] = _MISSING,
        flags: MessageFlags = MessageFlags(0),
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        suppress_notifications: bool = False,
        is_components_v2: bool = False,
    ) -> Message:
        if not self.acknowledged:
            raise InteractionNotResponded()

        if any((content, embeds, files)):
            if ephemeral:
                flags |= MessageFlags.EPHEMERAL
            if suppress_embeds:
                flags |= MessageFlags.SUPPRESS_EMBEDS
            if suppress_notifications:
                flags |= MessageFlags.SUPPRESS_NOTIFICATIONS
            if is_components_v2:
                flags |= MessageFlags.IS_COMPONENTS_V2

            return Message(
                await self._state.http.request(
                    Path(
                        "POST",
                        "webhooks/{webhook_id}/{webhook_token}",
                        webhook_id=self.application_id,
                        webhook_token=self.interaction_token,
                    ),
                    files=files,
                    json=assign_val_dict(
                        InteractionWebhookMessagePayload(
                            tts=tts, allowed_mentions=allowed_mentions._to_dict()
                        ),
                        _MISSING,
                        content=content,
                        embeds=(
                            [embed._to_dict() for embed in embeds]
                            if embeds is not _MISSING
                            else _MISSING
                        ),
                        attachments=(
                            [
                                file._to_attachment_dict(i)
                                for i, file in enumerate(files)
                            ]
                            if files is not _MISSING
                            else _MISSING
                        ),
                        flags=flags.value,
                    ),
                ),
                state=self._state,
            )

        raise ValueError("No sendable field was passed to the response")

    async def _webhook_messages_request(
        self,
        *,
        method: str,
        message: int | str = "@original",
        files: list[File] = _MISSING,
        **kwargs: Any,
    ) -> Any:
        return await self._state.http.request(
            Path(
                method,
                "webhooks/{webhook_id}/{webhook_token}/messages/{message}",
                webhook_id=self.application_id,
                webhook_token=self.interaction_token,
                message=str(message),
            ),
            files=files,
            **kwargs,
        )

    async def fetch_original_response(self) -> Message:
        return Message(
            await self._webhook_messages_request(method="GET"), state=self._state
        )

    async def edit_original_response(
        self,
        content: str | None = _MISSING,
        *,
        embeds: list[Embed] = _MISSING,
        flags: MessageFlags = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        files: list[File] = _MISSING,
        suppress_embeds: bool = _MISSING,
        is_components_v2: Literal[True] = _MISSING,
        override_files: bool = True,
    ) -> Message:
        if all(
            x is _MISSING
            for x in [
                content,
                embeds,
                flags,
                allowed_mentions,
                files,
                suppress_embeds,
                is_components_v2,
            ]
        ):
            raise ValueError("No editable fields were passed in editing response.")

        if suppress_embeds is not _MISSING or is_components_v2 is not _MISSING:
            flags = MessageFlags(0)
            if suppress_embeds:
                flags |= MessageFlags.SUPPRESS_EMBEDS
            if is_components_v2:
                flags |= MessageFlags.IS_COMPONENTS_V2

        return Message(
            await self._webhook_messages_request(
                method="PATCH",
                files=files,
                json=assign_val_dict(
                    InteractionWebhookMessagePayload(),
                    _MISSING,
                    content=content,
                    embeds=(
                        [embed._to_dict() for embed in embeds]
                        if embeds is not _MISSING
                        else _MISSING
                    ),
                    allowed_mentions=mtd(allowed_mentions),
                    attachments=(
                        [file._to_attachment_dict(i) for i, file in enumerate(files)]
                        if override_files and files is not _MISSING
                        else _MISSING
                    ),
                    flags=flags.value if flags is not _MISSING else _MISSING,
                ),
            ),
            state=self._state,
        )

    async def delete_original_response(self):
        await self._webhook_messages_request(method="DELETE")


class Interaction:
    __slots__ = (
        "_state",
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
        "attachment_size_limit",
    )

    def __init__(
        self,
        data: InteractionPayload,
        *,
        guild: Guild | None = None,
        state: ConnectionState,
    ):
        self._state = state
        self.id = Snowflake(data["id"])
        self.application_id = Snowflake(data["application_id"])
        self.type = InteractionType(data["type"])
        self.guild = guild
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.data = parse_interaction_data(
            self.type, data["data"], guild_id=self.guild_id, state=state
        )
        self.channel = (
            parse_channel_payload(c, partial=True, state=state)
            if (c := data.get("channel")) is not None
            else None
        )
        self.channel_id = Snowflake._from_str(data.get("channel_id"))
        self.member = scls(
            Member, data.get("member"), guild_id=self.guild_id, state=state
        )
        self.user = scls(User, data.get("user"), state=state)
        self.token = data["token"]
        self.version = data["version"]
        self.message = scls(Message, data.get("message"), state=state)
        self.app_permissions = Permissions(int(data["app_permissions"]))
        self.locale = data.get("locale")
        self.guild_locale = data.get("guild_locale")
        self.authorizing_integration_owners = {
            ApplicationIntegrationType(int(a)): (Snowflake(id) if id != "0" else 0)
            for a, id in data.get("authorizing_integration_owners", {}).items()
        }
        self.context = scls(InteractionContextType, data.get("context"))
        self.attachment_size_limit = data["attachment_size_limit"]

        self.response = ResponseHandler(
            self.id, self.token, self.application_id, state=state
        )
