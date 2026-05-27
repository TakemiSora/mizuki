from enum import IntEnum

class InteractionType(IntEnum):
   PING = 1
   APPLICATION_COMMAND = 2 
   MESSAGE_COMPONENT = 3
   APPLICATION_COMMAND_AUTOCOMPLETE = 4
   MODAL_SUBMIT = 5

class ApplicationIntegrationType(IntEnum):
   GUILD_INSTALL = 0
   USER_INSTALL = 1

class InteractionContextTypes(IntEnum):
   GUILD = 0
   BOT_DM = 1
   PRIVATE_CHANNEL = 2