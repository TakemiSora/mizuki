from ..payloads.embed import (
    EmbedAuthorPayload,
    EmbedFieldPayload,
    EmbedFooterPayload,
    EmbedMediaPayload,
    EmbedImagePayload,
    EmbedPayload,
    EmbedProviderPayload,
    EmbedVideoPayload
)
from ..enums.embed import (
    EmbedType
)
from ..flags import (
    EmbedMediaFlags,
    EmbedFlags
)
from ..utils import siso, scls

__all__ = (
    "Embed",
)

class EmbedFooter:
    __slots__ = (
        "text",
        "icon_url",
        "proxy_icon_url"
    )
    
    def __init__(self, data: EmbedFooterPayload):
        self.text = data["text"]
        self.icon_url = data.get("icon_url")
        self.proxy_icon_url = data.get("proxy_icon_url")

class EmbedMedia:
    __slots__ = (
        "proxy_url",
        "height",
        "width",
        "content_type",
        "placeholder",
        "placeholder_version",
        "description",
        "flags"
    )

    def __init__(self, data: EmbedMediaPayload):
        self.proxy_url = data.get("proxy_url")
        self.height = data.get("height")
        self.width = data.get("width")
        self.content_type = data.get("content_type")
        self.placeholder = data.get("placeholder")
        self.placeholder_version = data.get("placeholder_version")
        self.description = data.get("description")
        self.flags = EmbedMediaFlags(data.get("flags", 0))

class EmbedImage(EmbedMedia):
    __slots__ = (
        "url",
    )

    def __init__(self, data: EmbedImagePayload):
        super().__init__(data)
        self.url = data["url"]

class EmbedVideo(EmbedMedia):
    __slots__ = (
        "url",
    )

    def __init__(self, data: EmbedVideoPayload):
        super().__init__(data)
        self.url = data.get("url")

class EmbedProvider:
    __slots__ = (
        "name",
        "url"
    )

    def __init__(self, data: EmbedProviderPayload):
        self.name = data.get("name")
        self.url = data.get("url")

class EmbedAuthor:
    __slots__ = (
        "name",
        "url",
        "icon_url",
        "proxy_icon_url"
    )

    def __init__(self, data: EmbedAuthorPayload):
        self.name = data["name"]
        self.url = data.get("url")
        self.icon_url = data.get("icon_url")
        self.proxy_icon_url = data.get("proxy_icon_url")

class EmbedField:
    __slots__ = (
        "name",
        "value",
        "inline"
    )

    def __init__(self, data: EmbedFieldPayload):
        self.name = data["name"]
        self.value = data["value"]
        self.inline = data.get("inline", False)

class Embed:
    __slots__ = (
        "title",
        "type",
        "description",
        "url",
        "timestamp",
        "color",
        "footer",
        "image",
        "thumbnail",
        "video",
        "provider",
        "author",
        "fields",
        "flags"
    )
    
    def __init__(self, data: EmbedPayload):
        self.title = data.get("title")
        self.type = scls(EmbedType, data.get("type"))
        self.description = data.get("description")
        self.url = data.get("url")
        self.timestamp = siso(data.get("timestamp"))
        self.color = data.get("color")
        self.footer = scls(EmbedFooter, data.get("footer"))
        self.image = scls(EmbedImage, data.get("image"))
        self.thumbnail = scls(EmbedImage, data.get("thumbnail"))
        self.video = scls(EmbedVideo, data.get("video"))
        self.provider = scls(EmbedProvider, data.get("provider"))
        self.author = scls(EmbedAuthor, data.get("author"))
        self.fields = [EmbedField(f) for f in data.get("fields", [])]
        self.flags = EmbedFlags(data.get("flags", 0))