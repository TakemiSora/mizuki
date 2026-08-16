from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from mizuki._utils import (
    _MISSING,
    JSONPayload,
    assign_val,
    assign_val_dict,
    maybe_iter,
    mtd,
    parse_flags,
    scls,
)
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
from mizuki.objects.channel import PartialChannel, parse_channel_payload
from mizuki.objects.command import Localization
from mizuki.objects.components.resp_parser import parse_component_response
from mizuki.objects.embed import Embed
from mizuki.objects.guild import Guild
from mizuki.objects.member import Member
from mizuki.objects.message import AllowedMentions, Message
from mizuki.objects.modal import ModalResponse
from mizuki.objects.permissions import Permissions
from mizuki.objects.resolveddata import ResolvedData
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.user import User
from mizuki.payloads.interaction import (
    ApplicationCommandDataOptionPayload,
    ApplicationCommandDataPayload,
    AutocompleteChoicePayload,
    InteractionCallbackDataPayload,
    InteractionCallbackPayload,
    InteractionCallbackResourcePayload,
    InteractionCallbackResponsePayload,
    InteractionDataPayload,
    InteractionMessageCallbackDataPayload,
    InteractionPayload,
    InteractionWebhookMessagePayload,
)
from mizuki.payloads.modal import ModalResponsePayload

if TYPE_CHECKING:
    from mizuki.objects.components import Component, ComponentResponse
    from mizuki.objects.modal import Modal
    from mizuki.state import ConnectionState

__all__ = (
    "ApplicationCommandData",
    "ApplicationCommandDataOption",
    "AutocompleteChoice",
    "Interaction",
    "InteractionCallbackResponse",
    "ResponseHandler",
)


class AutocompleteChoice:
    """Represents an autocomplete choice to respond with to the autocomplete requests for command parameters."""

    __slots__ = ("name", "name_localizations", "value")

    name: str
    "The name of the choice."

    name_localizations: Localization | None
    "The localizations for the name of the choice."

    value: str | int | float
    "The value of this choice."

    def __init__(self, data: AutocompleteChoicePayload) -> None:
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.value = data["value"]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "name": self.name,
                "value": self.value,
            },
            name_localizations=mtd(self.name_localizations),
        )

    @classmethod
    def new(
        cls,
        *,
        name: str,
        value: str | int | float,  # noqa: PYI041
        name_localizations: Localization = _MISSING,
    ) -> AutocompleteChoice:
        """Returns an instance of a Autocomplete choice.

        Parameters
        ----------
        name : :class:`str`
            The name of the choice.

        value : :class:`str` | :class:`int` | :class:`float`
            The value for this choice.

        name_localizations : :class:`Localization <mizuki.objects.command.Localization>`, optional
            The localizations for the name of the choice.
        """
        return assign_val(
            cls({"name": name, "value": value}), name_localizations=name_localizations
        )


class ApplicationCommandDataOption[
    ValueType: str | int | float | bool = str | int | float | bool
]:
    """Represents an option in a ApplicationCommand that's invoked/being invoked."""

    type AnyApplicationCommandDataOptions = tuple[ApplicationCommandDataOption, ...]

    __slots__ = ("focused", "name", "options", "type", "value")

    name: str
    "The name of the option."

    type: CommandOptionType
    "The type of this option."

    value: ValueType | None
    "The value for this option that the user inputted."

    options: AnyApplicationCommandDataOptions
    "The nested options in this option, non-empty only in a SubGroup or SubGroupCommand type option."

    focused: bool
    "Returns ``True`` in an autocomplete response if the user is inputting this option/parameter."

    def __init__(self, data: ApplicationCommandDataOptionPayload) -> None:
        self.name = data["name"]
        self.type = CommandOptionType(data["type"])
        self.value = cast(ValueType, data.get("value"))
        self.options = tuple(
            ApplicationCommandDataOption(o) for o in data.get("options", [])
        )
        self.focused = data.get("focused", False)


class ApplicationCommandData[*OptionTypes = *tuple[ApplicationCommandDataOption, ...]]:
    """Represents an ApplicationCommand that's invoked/being invoked."""

    __slots__ = ("guild_id", "id", "name", "options", "resolved", "target_id", "type")

    type AnyOptionTypesApplicationCommandData = ApplicationCommandData[
        *ApplicationCommandDataOption.AnyApplicationCommandDataOptions
    ]

    id: Snowflake
    "The ID of the command."

    name: str
    "The name of the command."

    type: ApplicationCommandType
    "The type of the command."

    options: tuple[*OptionTypes]
    "The options for the command."

    guild_id: Snowflake | None
    "The guild ID of the guild the command was ran in."

    resolved: ResolvedData
    "The ID to object maps for this command."

    target_id: Snowflake | None
    "The ID of the object this command is targeted at, if the command is a context command."

    def __init__(
        self, data: ApplicationCommandDataPayload, *, state: ConnectionState
    ) -> None:
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.type = ApplicationCommandType(data["type"])
        self.options = cast(
            tuple[*OptionTypes],
            tuple(ApplicationCommandDataOption(o) for o in data.get("options", [])),
        )
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.resolved = ResolvedData(
            data.get("resolved", {}), guild_id=self.guild_id, state=state
        )
        self.target_id = Snowflake._from_str(data.get("target_id"))


class InteractionCallback:
    __slots__ = (
        "activity_instance_id",
        "id",
        "response_message_ephemeral",
        "response_message_id",
        "response_message_loading",
        "type",
    )

    def __init__(self, data: InteractionCallbackPayload):
        self.id = Snowflake(data["id"])
        self.type = InteractionType(data["type"])
        self.activity_instance_id = data.get("activity_instance_id")
        self.response_message_id = Snowflake._from_str(data.get("response_message_id"))
        self.response_message_loading = data.get("response_message_loading", False)
        self.response_message_ephemeral = data.get("response_message_ephemeral")


class InteractionCallbackResource:
    __slots__ = ("message", "type")

    def __init__(
        self, data: InteractionCallbackResourcePayload, *, state: ConnectionState
    ):
        self.type = InteractionCallbackType(data["type"])
        self.message = scls(Message, data.get("message"), state=state)


class InteractionCallbackResponse:
    __slots__ = ("interaction", "resource")

    def __init__(
        self, data: InteractionCallbackResponsePayload, *, state: ConnectionState
    ):
        self.interaction = InteractionCallback(data["interaction"])
        self.resource = InteractionCallbackResource(data["resource"], state=state)


def parse_interaction_data[*TypeData](
    type: InteractionType,
    data: InteractionDataPayload,
    *,
    guild_id: int | None,
    state: ConnectionState,
) -> ApplicationCommandData[*TypeData] | ComponentResponse | ModalResponse[*TypeData]:
    match type:
        case (
            InteractionType.APPLICATION_COMMAND
            | InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE
        ):
            return cast(
                ApplicationCommandData[*TypeData],
                ApplicationCommandData(
                    cast(ApplicationCommandDataPayload, data), state=state
                ),
            )
        case InteractionType.MESSAGE_COMPONENT:
            return parse_component_response(data, resolved_data=None, state=state)  # type: ignore # This is resolved.
        case InteractionType.MODAL_SUBMIT:
            return ModalResponse(
                cast(ModalResponsePayload, data), guild_id=guild_id, state=state
            )
        case _:
            raise UnknownInteractionType(f"Received unknown interaction type '{type}'")


class ResponseHandler:
    __slots__ = (
        "_state",
        "acknowledged",
        "application_id",
        "interaction_id",
        "interaction_token",
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
        **kwargs: Any,
    ) -> Any:
        return await self._state.http.request(
            Path(
                "POST",
                "interactions/{interaction_id}/{interaction_token}/callback",
                interaction_id=self.interaction_id,
                interaction_token=self.interaction_token,
            ),
            json={"type": type.value, "data": data},
            files=files,
            **kwargs,
        )

    async def send_response(
        self,
        content: str = _MISSING,
        *,
        tts: bool = False,
        embeds: list[Embed] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        files: list[File] = _MISSING,
        components: list[Component] = _MISSING,
        flags: MessageFlags = _MISSING,
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        suppress_notifications: bool = False,
        is_components_v2: bool = False,
        is_voice_message: bool = False,
    ) -> InteractionCallbackResponse:
        """Sends the first response to an interaction.

        Parameters
        ----------
        content : :class:`str`, optional
            The content of the message.

        tts : :class:`bool`, optional
            Whether the response is TTS.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`], optional
            The list of embeds to send along the response.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`, optional
            Controls which mentions trigger notifications.

        files : :class:`File <mizuki.file.File>`, optional
            The files to send along the response.

        components : list[:class:`Component <mizuki.objects.component.Component>`], optional
            The components to send along the message.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`, optional
            The flags for this message.

        ephemeral : :class:`bool`, optional
            Whether the response is ephemeral. Defaults to `False`.

        suppress_embeds : :class:`bool`, optional
            Whether the embeds are suppressed. Defaults to `False`.

        suppress_notifications : :class:`bool`, optional
            Whether the notifications are suppressed for this response. Defaults to `False`.

        is_components_v2 : :class:`bool`, optional
            Whether the :attr:`IS_COMPONENTS_V2 <mizuki.flags.MessageFlags.IS_COMPONENTS_V2>` is enabled. Defaults to `False`

        is_voice_message : :class:`bool`, optional
            Whether the message is a voice message.

        Raises
        ------
        `InteractionResponded`
            This interaction was already responded to.

        `HTTPException`
            An HTTP error occured.
        """
        if self.acknowledged:
            raise InteractionResponded()

        if any((content, embeds, files, components)):
            resp = InteractionCallbackResponse(
                await self._post(
                    type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                    files=files,
                    data=assign_val_dict(
                        InteractionMessageCallbackDataPayload(tts=tts),
                        _MISSING,
                        allowed_mentions=mtd(allowed_mentions),
                        content=content,
                        embeds=maybe_iter(embeds),
                        attachments=maybe_iter(
                            files,
                            enumerate_iter=True,
                            method=lambda i, a: a._to_attachment_dict(i),
                        ),
                        flags=parse_flags(
                            {
                                MessageFlags.EPHEMERAL: ephemeral,
                                MessageFlags.SUPPRESS_EMBEDS: suppress_embeds,
                                MessageFlags.SUPPRESS_NOTIFICATIONS: suppress_notifications,
                                MessageFlags.IS_COMPONENTS_V2: is_components_v2,
                                MessageFlags.IS_VOICE_MESSAGE: is_voice_message,
                            },
                            flag=MessageFlags,
                            instance=flags,
                        ),
                        components=maybe_iter(components),
                    ),
                    params={"with_response": "True"},
                ),
                state=self._state,
            )

            self.acknowledged = True

            assert resp.resource.message is not None
            self._state.register_components(resp.resource.message.id, components)

            return resp

        raise ValueError("No sendable field was passed to the response")

    async def send_modal(self, modal: Modal) -> InteractionCallbackResponse:
        """
        Sends a modal to an Interaction.

        Parameters
        ----------
        modal : :class:`Modal <mizuki.objects.modal.Modal>`
            The modal to send.

        Raises
        ------
        `InteractionResponded`
            This interaction was already responded to.

        `HTTPException`
            An HTTP error occured.
        """
        if self.acknowledged:
            raise InteractionResponded()

        resp = await self._post(InteractionCallbackType.MODAL, modal._to_dict())
        self._state.register_modal(modal)

        return InteractionCallbackResponse(resp, state=self._state)

    async def send_autocomplete_choices(self, *choices: AutocompleteChoice) -> None:
        """Send the autocomplete choices to give the user the choices they can use.

        Parameters
        ----------
        *choices : :class:`AutocompleteChoice`
            The choices to respond with.

        Raises
        ------
        `InteractionResponded`
            This interaction was already respnnded to.

        `HTTPException`
            An HTTP error occured.
        """
        if self.acknowledged:
            raise InteractionResponded()

        await self._post(
            InteractionCallbackType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT,
            {"choices": [c._to_dict() for c in choices]},
        )

    async def defer(self, *, ephemeral: bool = False) -> None:
        """Defers / Acknowledges the response.

        Parameters
        ----------
        ephemeral : class:`bool`, optional
            Whether the defer is ephemeral, defaults to ``False``.

        Raises
        ------
        `InteractionResponded`
            This interaction was already responded to.

        `HTTPException`
            An HTTP error occured.
        """
        if self.acknowledged:
            raise InteractionResponded()

        await self._post(
            InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
            {"flags": MessageFlags(MessageFlags.EPHEMERAL if ephemeral else 0)},
        )

        self.acknowledged = True

    async def send_followup(
        self,
        content: str = _MISSING,
        *,
        tts: bool = False,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        files: list[File] = _MISSING,
        flags: MessageFlags = _MISSING,
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        suppress_notifications: bool = False,
        is_components_v2: bool = False,
    ) -> Message:
        """Sends a followup response to an interaction.

        Parameters
        ----------
        content : :class:`str`, optional
            The content of the message.

        tts : :class:`bool`, optional
            Whether the response is TTS.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`], optional
            The list of embeds to send along the response.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`, optional
            Controls which mentions trigger notifications.

        files : :class:`File <mizuki.file.File>`, optional
            The files to send along the response.

        components : list[:class:`Component <mizuki.objects.component.Component>`], optional
            The components to send along the message.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`, optional
            The flags for this message.

        ephemeral : :class:`bool`, optional
            Whether the response is ephemeral. Defaults to `False`.

        suppress_embeds : :class:`bool`, optional
            Whether the embeds are suppressed. Defaults to `False`.

        suppress_notifications : :class:`bool`, optional
            Whether the notifications are suppressed for this response. Defaults to `False`.

        is_components_v2 : :class:`bool`, optional
            Whether the :attr:`IS_COMPONENTS_V2 <mizuki.flags.MessageFlags.IS_COMPONENTS_V2>` is enabled. Defaults to `False`

        Raises
        ------
        `InteractionNotResponded`
            This interaction was not yet responded to.

        `HTTPException`
            An HTTP error occured.
        """
        if not self.acknowledged:
            raise InteractionNotResponded()

        if any((content, embeds, files, components)):
            message = Message(
                await self._state.http.request(
                    Path(
                        "POST",
                        "webhooks/{webhook_id}/{webhook_token}",
                        webhook_id=self.application_id,
                        webhook_token=self.interaction_token,
                    ),
                    files=files,
                    json=assign_val_dict(
                        InteractionWebhookMessagePayload(tts=tts),
                        _MISSING,
                        allowed_mentions=mtd(allowed_mentions),
                        content=content,
                        embeds=maybe_iter(embeds),
                        components=maybe_iter(components),
                        attachments=maybe_iter(
                            files,
                            enumerate_iter=True,
                            method=lambda i, a: a._to_attachment_dict(i),
                        ),
                        flags=parse_flags(
                            {
                                MessageFlags.EPHEMERAL: ephemeral,
                                MessageFlags.SUPPRESS_EMBEDS: suppress_embeds,
                                MessageFlags.SUPPRESS_NOTIFICATIONS: suppress_notifications,
                                MessageFlags.IS_COMPONENTS_V2: is_components_v2,
                            },
                            flag=MessageFlags,
                            instance=flags,
                        ),
                    ),
                ),
                state=self._state,
            )

            self._state.register_components(message.id, components)
            return message

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
        """Fetches the original response of this interaction.

        Raises
        ------
        `NotFound`
            The interaction hasn't been responded to yet.

        `HTTPException`
            An HTTP error occured.
        """
        return Message(
            await self._webhook_messages_request(method="GET"), state=self._state
        )

    async def edit_original_response(
        self,
        content: str | None = _MISSING,
        *,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
        flags: MessageFlags = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        files: list[File] = _MISSING,
        suppress_embeds: bool = _MISSING,
        is_components_v2: Literal[True] = _MISSING,
        override_files: bool = True,
    ) -> Message:
        """Edits the original response to the interaction.

        Parameters
        ----------
        content : :class:`str` | :class:`None`, optional
            The content of the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`], optional
            The list of embeds of the message.

        components : list[:class:`Component <mizuki.objects.component.Component>`], optional
            The list of components of the message.

        flags : :class:`MessageFlags <mizuki.flags.Flags>`, optional
            The flags of this message.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`, optional
            Controls which mentions trigger notifications.

        files : :class:`File <mizuki.file.File>`, optional
            The files to send along the response.

        suppress_embeds : :class:`bool`, optional
            Whether the embeds are suppressed. Defaults to `False`.

        is_components_v2 : :class:`bool`, optional
            Whether the :attr:`IS_COMPONENTS_V2 <mizuki.flags.MessageFlags.IS_COMPONENTS_V2>` is enabled. Defaults to `False`

        override_files : :class:`bool`, optional
            Whether the files will be overriden or added to the current files.

        Raises
        ------
        `NotFound`
            This interaction was not yet responded to.

        `HTTPException`
            An HTTP error occured.
        """
        if all(
            x is _MISSING
            for x in [
                content,
                embeds,
                components,
                flags,
                allowed_mentions,
                files,
                suppress_embeds,
                is_components_v2,
            ]
        ):
            raise ValueError("No editable fields were passed in editing response.")

        message = Message(
            await self._webhook_messages_request(
                method="PATCH",
                files=files,
                json=assign_val_dict(
                    {},
                    _MISSING,
                    content=content,
                    embeds=maybe_iter(embeds),
                    components=maybe_iter(components),
                    allowed_mentions=mtd(allowed_mentions),
                    attachments=(
                        maybe_iter(
                            files,
                            enumerate_iter=True,
                            method=lambda i, a: a._to_attachment_dict(i),
                        )
                        if override_files
                        else _MISSING
                    ),
                    flags=parse_flags(
                        {
                            MessageFlags.SUPPRESS_EMBEDS: suppress_embeds,
                            MessageFlags.IS_COMPONENTS_V2: is_components_v2,
                        },
                        flag=MessageFlags,
                        instance=flags,
                    ),
                ),
            ),
            state=self._state,
        )

        self._state.register_components(message.id, components)
        return message

    async def delete_original_response(self) -> None:
        """Deletes the original response to the interaction.

        Raises
        ------
        `NotFound`
            The interaction hasn't been responded to yet.

        `HTTPError`
            An HTTP error occurred.
        """
        await self._webhook_messages_request(method="DELETE")


class Interaction[
    InteractionDataType: ApplicationCommandData | ComponentResponse | ModalResponse
]:
    """Represents an Interaction object from discord."""

    __slots__ = (
        "_state",
        "app_permissions",
        "application_id",
        "attachment_size_limit",
        "authorizing_integration_owners",
        "channel",
        "channel_id",
        "context",
        "data",
        "guild",
        "guild_id",
        "guild_locale",
        "id",
        "locale",
        "member",
        "message",
        "response",
        "token",
        "type",
        "user",
    )

    id: Snowflake
    "The ID of the interaction."

    application_id: Snowflake
    "The ID of the application this interaction is for."

    type: InteractionType
    "The type of the interaction."

    guild: Guild | None
    "The Guild that this interaction was sent from."

    guild_id: Snowflake | None
    "The ID of the Guild that this interaction was sent from."

    data: InteractionDataType
    "The data of the interaction"

    channel: PartialChannel | None
    "The channel that this interaction was sent from."

    channel_id: Snowflake
    "The ID of the channel this interaction was sent from."

    member: Member | None
    "The guild member that created this interaction."

    user: User
    "The user that created this interaction."

    token: str
    "The Interaction token."

    message: Message | None
    "For components or modals triggered by components, the message that they were attached to."

    app_permissions: Permissions
    "The permissions that the app has at the source of the interaction."

    locale: str
    "The locale of the invoking user."

    guild_locale: str | None
    "The locale of the guild this interaction was created in."

    authorizing_integration_owners: dict[ApplicationIntegrationType, Snowflake | int]
    "The dict with keys of ApplicationIntegrationTypes to the authorizing user or guild."

    context: InteractionContextType
    "The context where this interaction was triggered from."

    attachment_size_limit: int
    "The attachment size limit in bytes."

    response: ResponseHandler
    "The ResponseHandler for this interaction."

    def __init__(
        self,
        data: InteractionPayload,
        *,
        guild: Guild | None = None,
        state: ConnectionState,
    ) -> None:
        self._state = state
        self.id = Snowflake(data["id"])
        self.application_id = Snowflake(data["application_id"])
        self.type = InteractionType(data["type"])
        self.guild = guild
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.data = cast(
            InteractionDataType,
            parse_interaction_data(
                self.type, data["data"], guild_id=self.guild_id, state=state
            ),
        )
        self.channel = (
            parse_channel_payload(c, partial=True, state=state)
            if (c := data.get("channel")) is not None
            else None
        )
        self.channel_id = Snowflake(data["channel_id"])
        self.member = scls(
            Member, data.get("member"), guild_id=self.guild_id, state=state
        )
        if user := scls(User, data.get("user"), state=state) or (
            self.member if self.member is None else self.member.user
        ):
            self.user = user
        else:
            raise ValueError("Recieved malformed interaction payload.")

        self.token = data["token"]
        self.message = scls(Message, data.get("message"), state=state)
        self.app_permissions = Permissions(int(data["app_permissions"]))
        self.locale = data["locale"]
        self.guild_locale = data.get("guild_locale")
        self.authorizing_integration_owners = {
            ApplicationIntegrationType(int(a)): (Snowflake(id) if id != "0" else 0)
            for a, id in data.get("authorizing_integration_owners", {}).items()
        }
        self.context = InteractionContextType(data["context"])
        self.attachment_size_limit = data["attachment_size_limit"]

        self.response = ResponseHandler(
            self.id, self.token, self.application_id, state=state
        )
