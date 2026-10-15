from enum import StrEnum

__all__ = ("Event",)


class Event(StrEnum):
    """The Gateway Event enum to be provided in :meth:`Bot.listen() <mizuki.Bot.listen>`."""

    GUILD_CREATE = "on_guild_create"
    GUILD_UPDATE = "on_guild_update"
    GUILD_DELETE = "on_guild_delete"
    CHANNEL_CREATE = "on_channel_create"
    CHANNEL_UPDATE = "on_channel_update"
    CHANNEL_DELETE = "on_channel_delete"
    THREAD_CREATE = "on_thread_create"
    THREAD_UPDATE = "on_thread_update"
    THREAD_DELETE = "on_thread_delete"
    INTERACTION_CREATE = "on_interaction_create"
    READY = "on_ready"
