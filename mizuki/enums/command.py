from enum import IntEnum

__all__ = (
    "CommandOptionType",
    "ApplicationCommandType",
    "CommandHandler"
)

class CommandOptionType(IntEnum):
    SUB_COMMAND	= 1	
    SUB_COMMAND_GROUP = 2	
    STRING = 3	
    INTEGER	= 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11

class ApplicationCommandType(IntEnum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    PRIMARY_ENTRY_POINT = 4

class CommandHandler(IntEnum):
    APP_HANDLER = 1
    DISCORD_LAUNCH_ACTIVITY = 2