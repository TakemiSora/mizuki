from typing import TypedDict
from ._types import Snowflake, CDNHash


class AvatarDecorationPayload(TypedDict):
    sku_id: Snowflake
    asset: CDNHash
