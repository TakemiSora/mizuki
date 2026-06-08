from enum import IntEnum

__all__ = (
    "InteractionType",
    "ApplicationIntegrationType",
    "InteractionContextType"
)

class InteractionType(IntEnum):
   PING = 1
   APPLICATION_COMMAND = 2 
   MESSAGE_COMPONENT = 3
   APPLICATION_COMMAND_AUTOCOMPLETE = 4
   MODAL_SUBMIT = 5

class ApplicationIntegrationType(IntEnum):
   GUILD_INSTALL = 0
   USER_INSTALL = 1

class InteractionContextType(IntEnum):
   GUILD = 0
   BOT_DM = 1
   PRIVATE_CHANNEL = 2
   
class InteractionCallbackType(IntEnum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9
    LAUNCH_ACTIVITY = 12