from typing import TypedDict
from mizuki.payloads._types import Snowflake, CDNHash


class AvatarDecorationPayload(TypedDict):
    sku_id: Snowflake
    asset: CDNHash
