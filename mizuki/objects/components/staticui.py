from __future__ import annotations

from typing import TYPE_CHECKING

from mizuki._utils import _MISSING, JSONPayload, assign_val, assign_val_dict, scls
from mizuki.enums.components import ComponentType, SeparatorSpacing
from mizuki.flags import UnfurledMediaItemFlags
from mizuki.objects.components.actionrow import ActionRow
from mizuki.objects.components.button import Button
from mizuki.objects.components.common import BaseComponent, component_parser_gen
from mizuki.objects.snowflake import Snowflake

if TYPE_CHECKING:
    from mizuki.payloads.components import (
        ContainerPayload,
        FileComponentPayload,
        MediaGalleryItemPayload,
        MediaGalleryPayload,
        SectionChildComponentPayload,
        SectionPayload,
        SeparatorPayload,
        TextDisplayPayload,
        ThumbnailPayload,
        UnfurledMediaItemPayload,
    )

__all__ = (
    "TextDisplay",
    "UnfurledMediaItem",
    "Thumbnail",
    "Section",
    "MediaGallery",
    "FileComponent",
    "Separator",
    "Container",
)


class TextDisplay(BaseComponent):
    """
    Represents a TextDisplay component.
    """

    __slots__ = ("content",)

    content: str
    "The content of the TextDisplay."

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
    """
    Represents an UnfurledMediaItem.
    """

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

    url: str
    "The URL of the media item."

    proxy_url: str | None
    "The proxied URL of the media."

    height: int | None
    "The height of the media."

    width: int | None
    "The width of the media."

    placeholder: str | None
    "The thumbhash placeholder."

    placeholder_version: int | None
    "The version of the placeholder."

    flags: UnfurledMediaItemFlags | None
    "The media flags for the item."

    attachment_id: Snowflake | None
    "The ID of the uploaded attachment."

    def __init__(self, data: UnfurledMediaItemPayload):
        self.url = data["url"]
        self.proxy_url = data.get("proxy_url")
        self.height = data.get("height")
        self.width = data.get("width")
        self.placeholder = data.get("placeholder")
        self.placeholder_version = data.get("placeholder_version")
        self.flags = scls(UnfurledMediaItemFlags, data.get("flags"))
        self.attachment_id = Snowflake._from_str(data.get("attachment_id"))

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
    """
    Represents a Thumbnail component.
    """

    __slots__ = ("media", "description", "spoiler")

    media: UnfurledMediaItem
    "The media item of the thumbnail."

    description: str | None
    "The alt text for the media."

    spoiler: bool
    "Whether the image is spoilered."

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
        media : :class:`str` | :class:`UnfurledMediaItem`
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
    """
    Represents a Section component.
    """

    __slots__ = ("components", "accessory")

    components: list[SectionChildComponent]
    "The components of this section."

    accessory: SectionAccessoryComponent
    "The accessory of this section."

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
        """
        Returns an instance of a Section.

        Parameters
        ----------
        *components : :class:`SectionChildComponent`
            The components of this section.

        accessory : :class:`SectionAccessoryComponent`
            The accessory of this section.
        """
        return assign_val(
            cls({"type": 9, "components": [], "accessory": accessory._to_dict()}),
            components=components,
            id=id,
        )


class MediaGalleryItem:
    """
    Represents a MediaGallery item.
    """

    __slots__ = ("media", "description", "spoiler")

    media: UnfurledMediaItem
    "The media of this item."

    description: str | None
    "The alt text of the media."

    spoiler: bool
    "Whether this media item is spoilered."

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
        """
        Returns an instance of a MediaGalleryItem.

        Parameters
        ----------
        media : :class:`str` | :class:`UnfurledMediaItem`
            The URL or the media of the media gallery item.

        description : :class:`str`, optional
            The alt text for the media item, max 1024 characters.

        spoiler : :class:`bool`
            Whether the media item will be spoilered/blurred.
        """
        return assign_val(
            cls({"media": {"url": media if isinstance(media, str) else media.url}}),
            description=description,
            spoiler=spoiler,
        )


class MediaGallery(BaseComponent):
    """
    Represents a Media Gallery component.
    """

    __slots__ = ("items",)

    items: list[MediaGalleryItem]
    "The items of the media gallery."

    def __init__(self, data: MediaGalleryPayload):
        super().__init__(data)

        self.items = [MediaGalleryItem(d) for d in data["items"]]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 12, "items": [i._to_dict() for i in self.items]}, id=self.id
        )

    @classmethod
    def new(cls, *items: MediaGalleryItem, id: int = _MISSING) -> MediaGallery:
        """
        Returns an instance of a MediaGallery.

        Parameters
        ----------
        *items : :class:`MediaGalleryItem`
            The item(s) of the MediaGallery.

        id : :class:`int`, optional
            Optional unique identifier for the component.
        """
        return assign_val(cls({"type": 12, "items": []}), id=id, items=items)


class FileComponent(BaseComponent):
    """
    Represents a File component.
    """

    __slots__ = ("file", "spoiler", "name", "size")

    file: UnfurledMediaItem
    "The file for this component."

    spoiler: bool
    "Whether this file is spoilered."

    name: str | None
    "The name of the file."

    size: int | None
    "The size of the file in bytes."

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
        """
        Returns an instance of a File component.

        Parameters
        ----------
        file : :class:`str` | :class:`UnfurledMediaItem`
            The file for this component. Only supports the `attachment://{filename}` syntax URLs.

        id : :class:`int`, optional
            Optional unique identifier for this component.

        spoiler : :class:`bool`, optional
            Whether this media file is spoilered.
        """
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
    """
    Represents a Separator component.
    """

    __slots__ = ("divider", "spacing")

    divider: bool
    "Whether a visible divider is shown."

    spacing: SeparatorSpacing
    "The padding of the separator."

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
        """
        Returns an instance of a Separator component.

        Parameters
        ----------
        id : :class:`int`, optional
            Optional unique identifier for this component.

        divider : :class:`bool`, optional
            Whether a visible divider is shown for the component.

        spacing : :class:`SeparatorSpacing <mizuki.enums.components.SeparatorSpacing>`, optional
            The padding size of the separator.
        """
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
    """
    Represents a container component.
    """

    __slots__ = ("components", "accent_color", "spoiler")

    components: list[ContainerChildComponent]
    "The components of the container."

    accent_color: int | None
    "The accent color of the container."

    spoiler: bool
    "Whether this container is spoilered."

    def __init__(self, data: ContainerPayload):
        super().__init__(data)

        self.components = [parse_container_child(d) for d in data["components"]]
        self.accent_color = data.get("accent_color")
        self.spoiler = data.get("spoiler", False)

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"type": 17, "components": [c._to_dict() for c in self.components]},
            id=self.id,
            accent_color=self.accent_color,
            spoiler=self.spoiler or None,
        )

    @classmethod
    def new(
        cls,
        *components: ContainerChildComponent,
        id: int = _MISSING,
        accent_color: int = _MISSING,
        spoiler: bool = False,
    ) -> Container:
        """
        Returns an instance of a container componnet.

        Parameters
        ----------
        *components : :class:`ContainerChildComponent`
            The components for the container.

        id : :class:`int`, optional
            Optional unique identifier for the TextDisplay.

        accent_color : :class:`int`, optional
            The accent color for the container.

        spoiler : :class:`bool`, optional
            Whether the container will be spoilered.
        """
        return assign_val(
            cls({"type": 17, "components": []}),
            id=id,
            components=components,
            accent_color=accent_color,
            spoiler=spoiler,
        )
