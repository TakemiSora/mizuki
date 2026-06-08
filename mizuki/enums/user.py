from enum import IntEnum

__all__ = (
    "PremiumType",
)

class PremiumType(IntEnum):
    NONE = 0
    CLASSIC = 1
    NITRO = 2
    BASIC = 3