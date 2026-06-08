from typing import TypedDict, Literal, NotRequired
from ._types import Snowflake, CDNHash

class NameplatePayload(TypedDict):
    sku_id: Snowflake
    asset: CDNHash
    label: str
    palette: Literal["crimson", "berry", "sky", "teal", "forest", "bubble_gum", "violet", "cobalt", "clover", "lemon", "white"]

class CollectiblePayload(TypedDict):
    nameplate: NotRequired[NameplatePayload]