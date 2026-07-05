from enum import IntEnum

__all__ = ("InviteType", "InviteTargetType")


class InviteType(IntEnum):
    GUILD = 0
    GROUP_DM = 1
    FRIEND = 2


class InviteTargetType(IntEnum):
    STREAM = 1
    EMBEDDED_APPLICATION = 2
