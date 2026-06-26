from enum import StrEnum

__all__ = ("Event",)


class Event(StrEnum):
    """
    The Event enum to be provided in :meth:`Bot.listen() <mizuki.bot.Bot.listen>`.
    """

    GUILD_CREATE = "on_guild_create"
    "Dispatched when a guild is created or the bot joins a guild."

    GUILD_UPDATE = "on_guild_update"
    "Dispatched when a guild is updated."

    GUILD_DELETE = "on_guild_delete"
    "Dispatched when a guild is deleted or the bot leaves a guild."

    CHANNEL_CREATE = "on_channel_create"
    "Dispatched when a channel is created."

    CHANNEL_UPDATE = "on_channel_update"
    "Dispatched when a channel is updated."

    CHANNEL_DELETE = "on_channel_delete"
    "Dispatched when a channel is deleted."

    THREAD_CREATE = "on_thread_create"
    "Dispatched when a thread is created."

    THREAD_UPDATE = "on_thread_update"
    "Dispatched when a thread is updated."

    THREAD_DELETE = "on_thread_delete"
    "Dispatched when a thread is deleted."

    INTERACTION_CREATE = "on_interaction_create"
    "Dispatched when an interaction is created."

    READY = "on_ready"
    "Dispatched when the gateway is ready to send new events."
