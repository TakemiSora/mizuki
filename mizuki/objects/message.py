from __future__ import annotations
from datetime import datetime
from typing import Self, TYPE_CHECKING

from mizuki._utils import _MISSING, assign_val, assign_val_dict, scls, siso
from mizuki.enums.interaction import ApplicationIntegrationType
from mizuki.enums.interaction import InteractionType
from mizuki.enums.message import (
    BaseThemeType,
    MessageActivityType,
    MessageReferenceType,
    MessageType,
)
from mizuki.flags import AttachmentFlags, MessageFlags
from mizuki.objects.channel import ChannelMention, ThreadChannel
from mizuki.objects.embed import Embed
from mizuki.objects.emoji import PartialEmoji, Reaction
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.sticker import PartialSticker
from mizuki.objects.user import User
from mizuki.payloads.message import (
    AllowedMentionsPayload,
    AttachmentPayload,
    MessageActivityPayload,
    MessageInteractionMetadataPayload,
    MessagePayload,
    MessagePinPayload,
    MessageReferencePayload,
    MessageSnapshotPayload,
    PartialMessagePayload,
    PollAnswerCountPayload,
    PollAnswerPayload,
    PollMediaPayload,
    PollPayload,
    PollResultPayload,
    RoleSubscriptionDataPayload,
    SharedClientThemePayload,
)

if TYPE_CHECKING:
    from mizuki.state import ConnectionState
    from mizuki.file import File
    from mizuki.objects.components import Component

    from mizuki.enums.message import ReactionType

__all__ = (
    "Attachment",
    "MessageReference",
    "MessageActivity",
    "PartialMessage",
    "MessageSnapshot",
    "MessageInteractionMetadata",
    "RoleSubscriptionData",
    "PollMedia",
    "PollAnswer",
    "PollAnswerCount",
    "PollResult",
    "Poll",
    "SharedClientTheme",
    "AllowedMentions",
    "Message",
)


class Attachment:
    __slots__ = (
        "id",
        "filename",
        "title",
        "description",
        "content_type",
        "size",
        "url",
        "proxy_url",
        "height",
        "width",
        "placeholder",
        "placeholder_version",
        "ephemeral",
        "duration_secs",
        "waveform",
        "flags",
        "clip_participants",
        "clip_created_at",
        "application",
    )

    def __init__(self, data: AttachmentPayload, *, state: ConnectionState):
        self.id = Snowflake(data["id"])
        self.filename = data["filename"]
        self.title = data.get("title")
        self.description = data.get("description")
        self.content_type = data.get("content_type")
        self.size = data["size"]
        self.url = data["url"]
        self.proxy_url = data["proxy_url"]
        self.height = data.get("height")
        self.width = data.get("width")
        self.placeholder = data.get("placeholder")
        self.placeholder_version = data.get("placeholder_version")
        self.ephemeral = data.get("ephemeral", False)
        self.duration_secs = data.get("duration_secs")
        self.waveform = data.get("waveform")
        self.flags = AttachmentFlags(data.get("flags", 0))
        self.clip_participants = [
            User(u, state=state) for u in data.get("clip_participants", [])
        ]
        self.clip_created_at = siso(data.get("clip_created_at"))
        self.application = data.get("application")  # placeholder


class MessageReference:
    __slots__ = ("type", "message_id", "channel_id", "guild_id", "fail_if_not_exists")

    def __init__(self, data: MessageReferencePayload):
        self.type = MessageReferenceType(data.get("type", 0))
        self.message_id = Snowflake._from_str(data.get("message_id"))
        self.channel_id = Snowflake._from_str(data.get("channel_id"))
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.fail_if_not_exists = data.get("fail_if_not_exists", True)

    def _to_dict(self) -> MessageReferencePayload:
        return assign_val_dict(
            MessageReferencePayload(type=self.type.value),
            message_id=self.message_id,
            channel_id=self.channel_id,
            guild_id=self.guild_id,
            fail_if_not_exists=self.fail_if_not_exists,
        )

    @classmethod
    def new(
        cls,
        *,
        type: MessageReferenceType = MessageReferenceType.DEFAULT,
        message_id: int,
        channel_id: int = _MISSING,
        guild_id: int = _MISSING,
        fail_if_not_exists: bool = True,
    ) -> Self:
        return assign_val(
            cls(MessageReferencePayload(type=type.value)),
            message_id=message_id,
            channel_id=channel_id,
            guild_id=guild_id,
            fail_if_not_exists=fail_if_not_exists,
        )


class MessageActivity:
    __slots__ = ("type", "party_id")

    def __init__(self, data: MessageActivityPayload):
        self.type = MessageActivityType(data["type"])
        self.party_id = data.get("party_id")


class PartialMessage:
    __slots__ = (
        "_state",
        "content",
        "embeds",
        "attachments",
        "timestamp",
        "edited_timestamp",
        "flags",
        "mentions",
        "mention_roles",
        "type",
    )

    def __init__(self, data: PartialMessagePayload, *, state: ConnectionState):
        self._state = state
        self.content = data["content"]
        self.embeds = [Embed(e) for e in data["embeds"]]
        self.attachments = [Attachment(a, state=state) for a in data["attachments"]]
        self.timestamp = datetime.fromisoformat(data["timestamp"])
        self.edited_timestamp = siso(data["edited_timestamp"])
        self.flags = MessageFlags(data.get("flags", 0))
        self.mentions = [User(u, state=state) for u in data["mentions"]]
        self.mention_roles = [Snowflake(s) for s in data["mention_roles"]]
        self.type = MessageType(data["type"])


class MessageSnapshot:
    __slots__ = ("message",)

    def __init__(self, data: MessageSnapshotPayload, *, state: ConnectionState):
        self.message = PartialMessage(data["message"], state=state)


class MessageInteractionMetadata:
    __slots__ = (
        "id",
        "type",
        "user",
        "authorizing_integration_owners",
        "original_response_message_id",
        "target_user",
        "target_message_id",
    )

    def __init__(
        self, data: MessageInteractionMetadataPayload, *, state: ConnectionState
    ):
        self.id = Snowflake(data["id"])
        self.type = InteractionType(data["type"])
        self.user = User(data["user"], state=state)
        self.authorizing_integration_owners = {
            ApplicationIntegrationType(int(a)): Snowflake(s)
            for a, s in data["authorizing_integration_owners"].items()
        }
        self.original_response_message_id = Snowflake._from_str(
            data.get("original_response_message_id")
        )
        self.target_user = scls(User, data.get("target_user"), state=state)
        self.target_message_id = Snowflake._from_str(data.get("target_message_id"))


class RoleSubscriptionData:
    __slots__ = (
        "role_subscription_listing_id",
        "tier_name",
        "total_months_subscribed",
        "is_renewal",
    )

    def __init__(self, data: RoleSubscriptionDataPayload):
        self.role_subscription_listing_id = Snowflake(
            data["role_subscription_listing_id"]
        )
        self.tier_name = data["tier_name"]
        self.total_months_subscribed = data["total_months_subscribed"]
        self.is_renewal = data["is_renewal"]


class PollMedia:
    __slots__ = ("text", "emoji")

    def __init__(self, data: PollMediaPayload):
        self.text = data["text"]
        self.emoji = scls(PartialEmoji, data.get("emoji"))


class PollAnswer:
    __slots__ = ("answer_id", "poll_media")

    def __init__(self, data: PollAnswerPayload):
        self.answer_id = data["answer_id"]
        self.poll_media = PollMedia(data["poll_media"])


class PollAnswerCount:
    __slots__ = ("id", "count", "me_voted")

    def __init__(self, data: PollAnswerCountPayload):
        self.id = data["id"]
        self.count = data["count"]
        self.me_voted = data["me_voted"]


class PollResult:
    __slots__ = ("is_finalized", "answer_counts")

    def __init__(self, data: PollResultPayload):
        self.is_finalized = data["is_finalized"]
        self.answer_counts = [PollAnswerCount(p) for p in data["answer_counts"]]


class Poll:
    __slots__ = (
        "question",
        "answers",
        "expiry",
        "allow_multiselect",
        "layout_type",
        "results",
    )

    def __init__(self, data: PollPayload):
        self.question = PollMedia(data["question"])
        self.answers = [PollAnswer(p) for p in data["answers"]]
        self.expiry = siso(data["expiry"])
        self.allow_multiselect = data["allow_multiselect"]
        self.layout_type = data["layout_type"]
        self.results = scls(PollResult, data.get("results"))


class SharedClientTheme:
    __slots__ = ("colors", "gradient_angle", "base_mix", "base_theme")

    def __init__(self, data: SharedClientThemePayload):
        self.colors = data["colors"]
        self.gradient_angle = data["gradient_angle"]
        self.base_mix = data["base_mix"]
        self.base_theme = scls(BaseThemeType, data.get("base_theme"))


class AllowedMentions:
    __slots__ = ("parse",)

    def __init__(self, data: AllowedMentionsPayload):
        self.parse = data["parse"]

    def _to_dict(self) -> AllowedMentionsPayload:
        return AllowedMentionsPayload(parse=self.parse)

    @classmethod
    def new(
        cls, *, roles: bool = True, users: bool = True, everyone: bool = True
    ) -> Self:
        parse = []
        if roles:
            parse.append("roles")
        if users:
            parse.append("users")
        if everyone:
            parse.append("everyone")
        return cls(AllowedMentionsPayload(parse=parse))


class Message(PartialMessage):
    __slots__ = (
        "id",
        "channel_id",
        "author",
        "tts",
        "mention_everyone",
        "mention_channels",
        "reactions",
        "nonce",
        "pinned",
        "webhook_id",
        "activity",
        "application",
        "application_id",
        "message_reference",
        "message_snapshots",
        "referenced_message",
        "interaction_metadata",
        "thread",
        "components",
        "sticker_items",
        "position",
        "role_subscription_data",
        "poll",
        "shared_client_theme",
    )

    def __init__(self, data: MessagePayload, *, state: ConnectionState):
        super().__init__(data, state=state)
        self.id = Snowflake(data["id"])
        self.channel_id = Snowflake(data["channel_id"])
        self.author = User(data["author"], state=state)
        self.tts = data["tts"]
        self.mention_everyone = data["mention_everyone"]
        self.mention_channels = [
            ChannelMention(c) for c in data.get("mention_channels", [])
        ]
        self.reactions = [Reaction(r) for r in data.get("reactions", [])]
        self.nonce = data.get("nonce")
        self.pinned = data["pinned"]
        self.webhook_id = Snowflake._from_str(data.get("webhook_id"))
        self.activity = scls(MessageActivity, data.get("activity"))
        self.application = data.get("application")  # placehodler
        self.application_id = Snowflake._from_str(data.get("application_id"))
        self.message_reference = scls(MessageReference, data.get("message_reference"))
        self.message_snapshots = [
            MessageSnapshot(m, state=state) for m in data.get("message_snapshots", [])
        ]
        self.referenced_message = scls(
            Message, data.get("referenced_message"), state=state
        )
        self.interaction_metadata = scls(
            MessageInteractionMetadata, data.get("interaction_metadata"), state=state
        )
        self.thread = scls(ThreadChannel, data.get("thread"), state=state)
        self.components = data.get("components", [])  # placeholder
        self.sticker_items = [
            PartialSticker(s, state=state) for s in data.get("sticker_items", [])
        ]
        self.position = data.get("position")
        self.role_subscription_data = scls(
            RoleSubscriptionData, data.get("role_subscription_data")
        )
        self.poll = scls(Poll, data.get("poll"))
        self.shared_client_theme = scls(
            SharedClientTheme, data.get("shared_client_theme")
        )

    async def reply(
        self,
        content: str = _MISSING,
        *,
        tts: bool = _MISSING,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        files: list[File] = _MISSING,
        sticker_ids: list[int] = _MISSING,
        flags: MessageFlags = _MISSING,
    ) -> Message:
        """
        Creates a new reply to a message in the specified channel.

        .. note::

            At least one of, ``content``, ``embeds``, ``sticker_ids``, ``files`` must be provided.

        Parameters
        ----------
        content : :class:`str`
            The content of the message.

        tts : :class:`bool`
            Whether TTS is enabled for the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`]
            The list of embeds to send along the message.

        components : list[:class:`Component <mizuki.objects.component.Component>`]
            The list of components to send in this message.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled.

        files : list[:class:`File <mizuki.file.File>`]
            The files to upload with the message.

        sticker_ids : list[:class:`int`]
            The Guild Stickers to send with the message. Max 3.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`
            The MessageFlags of the new message.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to send to doesn't exist or the message you replied to doesn't exist.

        :class:`Forbidden`
            You are not allowed to send the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.reply(
            self.channel_id,
            self.id,
            content=content,
            tts=tts,
            embeds=embeds,
            components=components,
            allowed_mentions=allowed_mentions,
            files=files,
            sticker_ids=sticker_ids,
            flags=flags,
        )

    async def forward(
        self,
        target_channel_id: int,
    ) -> Message:
        """
        Forwards a message to a channel.

        Parameters
        ----------
        target_channel_id : :class:`int`
            The ID of the target Channel.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to send to doesn't exist or the message you tried to forward doesn't exist.

        :class:`Forbidden`
            You are not allowed to send the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.forward(
            target_channel_id,
            message_id=self.id,
            channel_id=self.channel_id,
        )

    async def crosspost(self) -> Message:
        """
        Crossposts a message from an Announcement Channel to all following channels.

        This requires :attr:`SEND_MESSAGES <mizuki.objects.permissions.Permissions.SEND_MESSAGES>` for your own messages, and
        :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>` when crossposting messages sent by others.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to crosspost from doesn't exist or the message you tried to crosspost doesn't exist.

        :class:`Forbidden`
            You are not allowed to crosspost the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.crosspost(self.channel_id, self.id)

    async def react(
        self,
        *,
        emoji_id: int = _MISSING,
        emoji_name: str,
    ) -> None:
        """
        Adds a reaction to a message.

        Requires :attr:`READ_MESSAGE_HISTORY <mizuki.objects.permissions.Permissions.READ_MESSAGE_HISTORY>`. Also requires :attr:`ADD_REACTIONS <mizuki.objects.permissions.Permissions.ADD_REACTIONS>` if no one has reacted with this emoji.

        Parameters
        ----------
        emoji_id : :class:`int`, optional
            The ID of the custom emoji. Omit when reacting with a unicode emoji.

        emoji_name : :class:`str`
            The unicode emoji or the name of the custom emoji.

        Raises
        ------
        :class:`NotFound`
            The message you tried to react to or the emoji you tried to react with wasn't found.

        :class:`Forbidden`
            You are not allowed to react/see the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.react(
            channel_id=self.channel_id,
            message_id=self.id,
            emoji_id=emoji_id,
            emoji_name=emoji_name,
        )

    async def remove_reaction(
        self,
        *,
        user_id: int = _MISSING,
        emoji_id: int = _MISSING,
        emoji_name: str,
    ) -> None:
        """
        Removes your reaction from a message.

        Parameters
        ----------
        user_id : :class:`int`, optional
            The ID of the target user. Defaults to client user.

        emoji_id : :class:`int`, optional
            The ID of the custom emoji. Omit when reacting with a unicode emoji.

        emoji_name : :class:`str`
            The unicode emoji or the name of the custom emoji.

        Raises
        ------
        :class:`NotFound`
            The message you tried to remove reaction from or the emoji you tried to remove reaction of wasn't found.

        :class:`Forbidden`
            You are not allowed to remove reaction/see the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.remove_reaction(
            channel_id=self.channel_id,
            message_id=self.id,
            user_id=user_id,
            emoji_id=emoji_id,
            emoji_name=emoji_name,
        )

    async def remove_all_reactions(self) -> None:
        """
        Removes all reactions from a message. This method requires :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>`.

        Raises
        ------
        :class:`NotFound`
            The message you tried to do this action on does not exist.

        :class:`Forbidden`
            You are not allowed to fetch the message. Or you are missing the permissions to do this action.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.remove_all_reactions(
            channel_id=self.channel_id, message_id=self.id
        )

    async def fetch_reactions(
        self,
        *,
        emoji_id: int = _MISSING,
        emoji_name: str,
        type: ReactionType = _MISSING,
        after: int = _MISSING,
        limit: int = _MISSING,
    ) -> list[User]:
        """
        Fetch a list of users that reacted with this emoji.

        Parameters
        ----------
        emoji_id : :class:`int`, optional
            The ID of the custom emoji. Omit when reacting with a unicode emoji.

        emoji_name : :class:`str`
            The unicode emoji or the name of the custom emoji.

        type : :class:`ReactionType <mizuki.enums.message.ReactionType>`, optional
            The type of the reaction to fetch. Defaults to fetches :attr:`NORMAL <mizuki.enums.message.ReactionType.NORMAL>`.

        after : :class:`int`, optional
            To fetch the list starting after the specified user ID.

        limit : :class:`int`, optional
            The max number of users to retrieve. Can be 1-100. Defaults to 25.

        Raises
        ------
        :class:`NotFound`
            The message you tried to fetch reactions of could not be found.

        :class:`Forbidden`
            You are not allowed to fetch the message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.fetch_reactions(
            channel_id=self.channel_id,
            message_id=self.id,
            emoji_id=emoji_id,
            emoji_name=emoji_name,
            type=type,
            after=after,
            limit=limit,
        )

    async def edit(
        self,
        content: str | None = _MISSING,
        *,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
        flags: MessageFlags = _MISSING,
        allowed_mentions: AllowedMentions | None = _MISSING,
        files: list[File] = _MISSING,
        override_files: bool = True,
    ) -> Message:
        """
        Edits a message sent by you.

        Parameters
        ----------
        content : :class:`str`
            The content of the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`]
            The embeds of the message.

        components : list[Component <mizuki.objects.component.Component>]
            The list of components.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`
            The flags of the message.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>` | :class:`None`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled. Pass ``None`` to set this back to default.

        files : list[:class:`File <mizuki.file.File>`]
            The files to upload to the message.

        override_files : :class:`bool`
            Whether to override or append the files to the message. Description is ignored when this is set to ``False``

        Raises
        ------
        :class:`NotFound`
            The message you tried to edit was not found.

        :class:`Forbidden`
            You are not allowed to edit that message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.edit(
            channel_id=self.channel_id,
            message_id=self.id,
            content=content,
            embeds=embeds,
            components=components,
            flags=flags,
            allowed_mentions=allowed_mentions,
            files=files,
            override_files=override_files,
        )

    async def delete(self) -> None:
        """
        Deletes a message from a channel.

        This method requires :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>` if deleting a message from someone else.

        Raises
        ------
        :class:`NotFound`
            The message you tried to delete does not exist.

        :class:`Forbidden`
            You are not allowed to delete that message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        await self._state.managers.messages.delete(
            channel_id=self.channel_id, message_id=self.id
        )


class MessagePin:
    __slots__ = ("pinned_at", "message")

    def __init__(self, data: MessagePinPayload, *, state: ConnectionState):
        self.pinned_at = datetime.fromisoformat(data["pinned_at"])
        self.message = Message(data["message"], state=state)
