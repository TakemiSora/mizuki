from typing import TypedDict, Literal, NotRequired

class NameplatePayload(TypedDict):
    sku_id: str
    asset: str
    label: str
    palette: Literal["crimson", "berry", "sky", "teal", "forest", "bubble_gum", "violet", "cobalt", "clover", "lemon", "white"]

class CollectiblePayload(TypedDict):
    nameplate: NotRequired[NameplatePayload]