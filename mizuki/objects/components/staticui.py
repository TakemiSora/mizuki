from __future__ import annotations
from typing import TYPE_CHECKING

from mizuki._utils import JSONPayload, assign_val, assign_val_dict, scls, _MISSING
from mizuki.enums.components import ComponentType, SeparatorSpacing
from mizuki.flags import UnfurledMediaItemFlags
from mizuki.objects.components.common import BaseComponent, component_parser_gen
from mizuki.objects.components.actionrow import ActionRow
from mizuki.objects.components.button import Button

if TYPE_CHECKING:
    from mizuki.payloads.components import (
        FileComponentPayload,
        TextDisplayPayload,
        UnfurledMediaItemPayload,
        ThumbnailPayload,
        MediaGalleryItemPayload,
        MediaGalleryPayload,
        SectionChildComponentPayload,
        SectionPayload,
        SeparatorPayload,
        ContainerPayload,
    )

__all__ = (
    "TextDisplay",
    "UnfurledMediaItem",
    "Thumbnail",
    "Section",
    "MediaGallery",
    "FileComponent",
    "Separator",
    "Container"
)


class TextDisplay(BaseComponent):
    __slots__ = ("content",)

    def __init__(self, data: TextDisplayPayload):
        super().__init__(data)

        self.content = data["content"]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict({"type": 10, "content": self.content}, id=self.id)

    @classmethod
    def new(cls, content: str, *, id: int = _MISSING) -> TextDisplay:
        """
        Returns a TextDisplay instance.

        Parameters
        ----------
        content : :class:`str`
            The content of the TextDisplay.

        id : :class:`int`, optional
            Optional unique identifier for the TextDisplay.
        """
        return assign_val(cls({"type": 10, "content": content}), id=id)


class UnfurledMediaItem:
    __slots__ = (
        "url",
        "proxy_url",
        "height",
        "width",
        "placeholder",
        "placeholder_version",
        "content_type",
        "flags",
        "attachment_id",
    )

    def __init__(self, data: UnfurledMediaItemPayload):
        self.url = data["url"]
        self.proxy_url = data.get("proxy_url")
        self.height = data.get("height")
        self.width = data.get("width")
        self.placeholder = data.get("placeholder")
        self.placeholder_version = data.get("placeholder_version")
        self.flags = scls(UnfurledMediaItemFlags, data.get("flags"))
        self.attachment_id = data.get("attachment_id")

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"url": self.url},
            proxy_url=self.proxy_url,
            height=self.height,
            width=self.width,
            placeholder=self.placeholder,
            placeholder_version=self.placeholder_version,
            flags=(self.flags.value if self.flags is not None else None),
            attachment_id=self.attachment_id,
        )

    @classmethod
    def new(cls, url: str) -> UnfurledMediaItem:
        """
        Returns an UnfurledMediaItem instance.

        Parameters
        ----------
        url : :class:`str`
            The URL of the media. Supports arbitary URLs and `attachement://<file>` format.
        """
        return cls({"url": url})


class Thumbnail(BaseComponent):
    __slots__ = ("media", "description", "spoiler")

    def __init__(self, data: ThumbnailPayload):
        super().__init__(data)

        self.media = UnfurledMediaItem(data["media"])
        self.description = data.get("description")
        self.spoiler = data.get("spoiler", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 11, "media": self.media._to_dict()},
            id=self.id,
            description=self.description,
            spoiler=self.spoiler or None,
        )

    @classmethod
    def new(
        cls,
        media: str | UnfurledMediaItem,
        *,
        id: int = _MISSING,
        description: str = _MISSING,
        spoiler: bool = False,
    ) -> Thumbnail:
        """
        Returns a Thumbnail instance.

        Parameters
        ----------
        media : :class:`str` | :class:`UnfurledMediaItem <mizuki.objects.components.staticui.UnfurledMediaItem>`
            The URL or the UnfurledMediaItem for the Thumbnail.

        id : :class:`int`, optional
            Optional unique identifier for the Thumbnail.

        description : :class:`str`, optional
            Alt text for the Thumbnail.

        spoiler : :class:`bool`, optional
            Whether the Thumbnail is spoilered.
        """
        return assign_val(
            cls(
                {
                    "media": {"url": media if isinstance(media, str) else media.url},
                    "type": 11,
                }
            ),
            id=id,
            description=description,
            spoiler=spoiler,
        )


type SectionChildComponent = TextDisplay
type SectionAccessoryComponent = Button | Thumbnail

SECTION_ACCESSORY_MAP: dict[ComponentType, type[SectionAccessoryComponent]] = {
    ComponentType.BUTTON: Button,
    ComponentType.THUMBNAIL: Thumbnail,
}


def parse_section_child(data: SectionChildComponentPayload) -> SectionChildComponent:
    # Right now discord only allows textdisplay here
    return TextDisplay(data)


parse_section_accessory = component_parser_gen(
    SECTION_ACCESSORY_MAP, "Section Accessory"
)


class Section(BaseComponent):
    __slots__ = ("components", "accessory")

    def __init__(self, data: SectionPayload):
        super().__init__(data)

        self.components = [parse_section_child(d) for d in data["components"]]
        self.accessory = parse_section_accessory(data["accessory"])

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": 9,
                "components": [c._to_dict() for c in self.components],
                "accessory": self.accessory._to_dict(),
            },
            id=self.id,
        )

    @classmethod
    def new(
        cls,
        *components: SectionChildComponent,
        accessory: SectionAccessoryComponent,
        id: int = _MISSING,
    ) -> Section:
        return assign_val(
            cls({"type": 9, "components": [], "accessory": accessory._to_dict()}),
            components=components,
            id=id,
        )


class MediaGalleryItem:
    __slots__ = ("media", "description", "spoiler")

    def __init__(self, data: MediaGalleryItemPayload):
        self.media = UnfurledMediaItem(data["media"])
        self.description = data.get("description")
        self.spoiler = data.get("spoiler", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"media": self.media._to_dict()},
            description=self.description,
            spoiler=self.spoiler or None,
        )

    @classmethod
    def new(
        cls,
        media: str | UnfurledMediaItem,
        *,
        description: str = _MISSING,
        spoiler: bool = False,
    ) -> MediaGalleryItem:
        return assign_val(
            cls({"media": {"url": media if isinstance(media, str) else media.url}}),
            description=description,
            spoiler=spoiler,
        )


class MediaGallery(BaseComponent):
    __slots__ = ("items",)

    def __init__(self, data: MediaGalleryPayload):
        super().__init__(data)

        self.items = [MediaGalleryItem(d) for d in data["items"]]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 12, "items": [i._to_dict() for i in self.items]}, id=self.id
        )

    @classmethod
    def new(cls, *items: MediaGalleryItem, id: int = _MISSING) -> MediaGallery:
        return assign_val(cls({"type": 12, "items": []}), id=id, items=items)


class FileComponent(BaseComponent):
    __slots__ = ("file", "spoiler", "name", "size")

    def __init__(self, data: FileComponentPayload):
        super().__init__(data)

        self.file = UnfurledMediaItem(data["file"])
        self.spoiler = data.get("spoiler", False)
        self.name = data.get("name")
        self.size = data.get("size")

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": 13,
                "file": self.file._to_dict(),
            },
            id=self.id,
            spoiler=self.spoiler or False,
            name=self.name,
            size=self.size,
        )

    @classmethod
    def new(
        cls, file: str | UnfurledMediaItem, *, id: int = _MISSING, spoiler: bool = False
    ) -> FileComponent:
        return assign_val(
            cls(
                {
                    "type": 13,
                    "file": {"url": file if isinstance(file, str) else file.url},
                }
            ),
            id=id,
            spoiler=spoiler,
        )


class Separator(BaseComponent):
    __slots__ = ("divider", "spacing")

    def __init__(self, data: SeparatorPayload):
        super().__init__(data)

        self.divider = data.get("divider", True)
        self.spacing = SeparatorSpacing(data.get("spacing", 1))

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 14, "divider": self.divider, "spacing": self.spacing.value},
            id=self.id,
        )

    @classmethod
    def new(
        cls,
        *,
        id: int = _MISSING,
        divider: bool = True,
        spacing: SeparatorSpacing = SeparatorSpacing.SMALL,
    ) -> Separator:
        return assign_val(
            cls({"type": 14, "divider": divider, "spacing": spacing.value}), id=id
        )


type ContainerChildComponent = (
    ActionRow | TextDisplay | Section | MediaGallery | Separator | FileComponent
)

CONTAINER_CHILD_MAP: dict[ComponentType, type[ContainerChildComponent]] = {
    ComponentType.ACTION_ROW: ActionRow,
    ComponentType.TEXT_DISPLAY: TextDisplay,
    ComponentType.SECTION: Section,
    ComponentType.MEDIA_GALLERY: MediaGallery,
    ComponentType.SEPARATOR: Separator,
    ComponentType.FILE: FileComponent,
}

parse_container_child = component_parser_gen(CONTAINER_CHILD_MAP, "Container")

class Container(BaseComponent):
    __slots__ = ("components", "accent_color", "spoiler")

    def __init__(self, data: ContainerPayload):
        super().__init__(data)

        self.components = [parse_container_child(d) for d in data["components"]]
        self.accent_color = data.get("accent_color")
        self.spoiler = data.get("spoiler", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": 17,
                "components": [c._to_dict() for c in self.components]
            },
            id=self.id,
            accent_color=self.accent_color,
            spoiler=self.spoiler or None
        )

    @classmethod
    def new(
        cls, *components: ContainerChildComponent,
        id: int = _MISSING,
        accent_color: int = _MISSING,
        spoiler: bool = False
    ) -> Container:
        return assign_val(
            cls({
                "type": 17,
                "components": []
            }),
            id=id,
            components=components,
            accent_color=accent_color,
            spoiler=spoiler
        )