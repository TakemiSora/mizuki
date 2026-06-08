from datetime import datetime
from typing import Self

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
from .._utils import mtd, siso, scls, assign_val, assign_val_dict, _MISSING

__all__ = (
    "EmbedFooter",
    "EmbedImage",
    "EmbedAuthor",
    "EmbedField",
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

    def _to_dict(self) -> EmbedFooterPayload:
        return assign_val_dict(
            EmbedFooterPayload(text=self.text),
            icon_url=self.icon_url
        )

    @classmethod
    def new(
        cls, *,
        text: str,
        icon_url: str = _MISSING
    ) -> Self:
        footer = cls(EmbedFooterPayload(text=text))
        footer.icon_url = icon_url
        return assign_val(
            cls(EmbedFooterPayload(
                text=text
            )),
            icon_url=icon_url
        )

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

    def _to_dict(self) -> EmbedImagePayload:
        return EmbedImagePayload(url=self.url)

    @classmethod
    def new(cls, url: str) -> Self:
        return cls(EmbedImagePayload(url=url))

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
        
    def _to_dict(self) -> EmbedAuthorPayload:
        return assign_val_dict(
            EmbedAuthorPayload(
                name=self.name
            ),
            url=self.url,
            icon_url=self.icon_url
        )

    @classmethod
    def new(
        cls, *,
        name: str,
        url: str = _MISSING,
        icon_url: str = _MISSING,
    ) -> Self:
        return assign_val(
            cls(EmbedAuthorPayload(
                name=name
            )),
            url=url,
            icon_url=icon_url
        )

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

    def _to_dict(self) -> EmbedFieldPayload:
        return EmbedFieldPayload(
            name=self.name,
            value=self.value,
            inline=self.inline
        )

    @classmethod
    def new(
        cls, *,
        name: str,
        value: str,
        inline: bool = False
    ) -> Self:
        return cls(EmbedFieldPayload(
            name=name,
            value=value,
            inline=inline
        ))

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
        self.type = EmbedType(data.get("type", "rich"))
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

    def _to_dict(self) -> EmbedPayload:
        return assign_val_dict(
            EmbedPayload(),
            title=self.title,
            type=self.type.value,
            description=self.description,
            timestamp=self.timestamp.isoformat() if self.timestamp is not None else None,
            color=self.color,
            footer=mtd(self.footer),
            image=mtd(self.image),
            thumbnail=mtd(self.thumbnail),
            author=mtd(self.author),
            fields=[f._to_dict() for f in self.fields] if self.fields else None
        )

    @classmethod
    def new(
        cls, *,
        title: str = _MISSING,
        description: str = _MISSING,
        timestamp: datetime = _MISSING,
        color: int = _MISSING,
        footer: EmbedFooter = _MISSING,
        image: EmbedImage = _MISSING,
        thumbnail: EmbedImage = _MISSING,
        author: EmbedAuthor = _MISSING,
        fields: list[EmbedField] = _MISSING
    ) -> Self:
        return assign_val(
            cls(EmbedPayload(type=EmbedType.rich)),
            title=title,
            description=description,
            timestamp=timestamp,
            color=color,
            footer=footer,
            image=image,
            thumbnail=thumbnail,
            author=author,
            fields=fields
        )