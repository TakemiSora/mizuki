from mizuki.objects.asset import Asset
from mizuki.objects.snowflake import Snowflake
from mizuki.payloads.avatar_decoration import AvatarDecorationPayload

__all__ = ("AvatarDecoration",)


class AvatarDecoration:
    """
    Represents a :class:`User <mizuki.objects.user.User>`'s Avatar Decoration.
    """

    sku_id: Snowflake
    "The Sku ID of this AvatarDecoration."

    asset: Asset
    "The Asset of the AvatarDecoration."

    __slots__ = ("sku_id", "asset")

    def __init__(self, data: AvatarDecorationPayload):
        self.sku_id = Snowflake(data["sku_id"])
        self.asset = Asset._from_user_avatar_decoration(data["asset"])

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.sku_id == obj.sku_id
        return NotImplemented

    def __hash__(self) -> int:
        return self.sku_id
