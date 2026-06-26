from typing import Self

from ..enums.sticker import StickerFormatType

__all__ = ("Asset", "MediaProxyAsset")


class Asset:
    """
    Represents a Discord CDN Asset.

    Parameters
    ----------
    url : :class:`str`
        The URL of the Asset.
    animated : :class:`bool`
        Represents if an Asset is animated.
    """

    url: str
    "The URL of the Asset."

    animated: bool
    "Represents if an Asset is animated."

    __slots__ = ("url", "animated")

    CDN_URL = "https://cdn.discordapp.com"
    "The base CDN URL."

    def __init__(self, url: str, animated: bool):
        self.url = url
        self.animated = animated

    def __str__(self) -> str:
        return self.url

    @classmethod
    def _from_user_avatar(cls, user_id: int, avatar_hash: str | None) -> Self | None:
        if avatar_hash is not None:
            is_animated = avatar_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/avatars/{user_id}/{avatar_hash}.webp{'?animated=true' if is_animated else ''}",
                is_animated,
            )
        return None

    @classmethod
    def _from_user_banner(cls, user_id: int, banner_hash: str | None) -> Self | None:
        if banner_hash is not None:
            is_animated = banner_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/banners/{user_id}/{banner_hash}.webp{'?animated=true' if is_animated else ''}",
                is_animated,
            )
        return None

    @classmethod
    def _from_user_avatar_decoration(cls, avatar_decoration_hash: str) -> Self:
        is_animated = avatar_decoration_hash.startswith("a_")
        return cls(
            f"{cls.CDN_URL}/avatar-decoration-presets/{avatar_decoration_hash}.png",
            is_animated,
        )

    @classmethod
    def _from_collectibles_nameplate(cls, nameplate_asset: str) -> Self:
        return cls(
            f"{cls.CDN_URL}/assets/collectibles/{nameplate_asset}asset.webm", True
        )

    @classmethod
    def _from_guild_avatar(cls, guild_id: int, avatar_hash: str | None) -> Self | None:
        if avatar_hash is not None:
            is_animated = avatar_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/icons/{guild_id}/{avatar_hash}.webp{'?animated=true' if is_animated else ''}",
                is_animated,
            )
        return None

    @classmethod
    def _from_guild_splash(cls, guild_id: int, splash_hash: str | None) -> Self | None:
        if splash_hash is not None:
            return cls(f"{cls.CDN_URL}/splashes/{guild_id}/{splash_hash}.webp", False)
        return None

    @classmethod
    def _from_guild_discovery_splash(
        cls, guild_id: int, splash_hash: str | None
    ) -> Self | None:
        if splash_hash is not None:
            return cls(
                f"{cls.CDN_URL}/discovery-splashes/{guild_id}/{splash_hash}.webp", False
            )
        return None

    @classmethod
    def _from_guild_tag_badge(
        cls, guild_id: int | None, badge_hash: str | None
    ) -> Self | None:
        if guild_id is not None and badge_hash is not None:
            return cls(
                f"{cls.CDN_URL}/guild-tag-badges/{guild_id}/{badge_hash}.webp", False
            )
        return None

    @classmethod
    def _from_role_icon(cls, role_id: int, role_hash: str | None) -> Self | None:
        if role_hash is not None:
            return cls(f"{cls.CDN_URL}/role-icons/{role_id}/{role_hash}.webp", False)
        return None

    @classmethod
    def _from_custom_emoji(cls, emoji_id: int | None, is_animated: bool) -> Self | None:
        if emoji_id is not None:
            return cls(
                f"{cls.CDN_URL}/emojis/{emoji_id}.webp{'?animated=true' if is_animated else ''}",
                is_animated,
            )
        return None

    @classmethod
    def _from_guild_banner(cls, guild_id: int, banner_hash: str | None) -> Self | None:
        if banner_hash is not None:
            is_animated = banner_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/guilds/{guild_id}/{banner_hash}.webp{'?animated=true' if is_animated else ''}",
                is_animated,
            )
        return None

    @classmethod
    def _from_sticker(cls, sticker_type: StickerFormatType, sticker_id: int) -> Self:
        is_animated = sticker_type != StickerFormatType.PNG
        return cls(
            f"{cls.CDN_URL}/stickers/{sticker_id}.{str(sticker_type)}", is_animated
        )

    @classmethod
    def _from_member_avatar(
        cls, guild_id: int, member_id: int | None, member_avatar_hash: str | None
    ) -> Self | None:
        if member_id is not None and member_avatar_hash is not None:
            is_animated = member_avatar_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/guilds/{guild_id}/users/{member_id}/avatars/{member_avatar_hash}.webp{'?animated=true' if is_animated else ''}",
                is_animated,
            )
        return None

    @classmethod
    def _from_member_banner(
        cls, guild_id: int, member_id: int | None, member_banner_hash: str | None
    ) -> Self | None:
        if member_id is not None and member_banner_hash is not None:
            is_animated = member_banner_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/guilds/{guild_id}/users/{member_id}/banners/{member_banner_hash}.webp{'?animated=true' if is_animated else ''}",
                is_animated,
            )
        return None

    @classmethod
    def _from_application_asset(
        cls, application_id: int | None, asset_hash: str | None
    ) -> Self | None:
        if application_id is not None and asset_hash is not None:
            return cls(f"{cls.CDN_URL}/app-assets/{application_id}/{asset_hash}", False)
        return None

    @classmethod
    def _from_guild_scheduled_event_cover(
        cls, event_id: int, cover_hash: str | None
    ) -> Self | None:
        if cover_hash is not None:
            return cls(
                f"{cls.CDN_URL}/guild-events/{event_id}/{cover_hash}.webp", False
            )
        return None


class MediaProxyAsset:
    """
    Represents a discord MediaProxyAsset.

    Parameters
    ----------
    url : :class:`str`
        The URL of the Asset.
    """

    url: str
    "The URL of the Asset."

    __slots__ = ("url",)

    MEDIA_URL = "https://media.discordapp.net"
    "The base URL."

    def __init__(self, url: str):
        self.url = url

    @classmethod
    def _from_image_id(cls, image_id: str | None) -> Self | None:
        if image_id is not None:
            return cls(f"{cls.MEDIA_URL}/{image_id}")
        return None


def activity_asset_parse(
    application_id: int | None, avatar_hash: str | None
) -> MediaProxyAsset | Asset | None:
    ":meta private:"
    if avatar_hash is not None:
        if avatar_hash.startswith("mp:"):
            return MediaProxyAsset._from_image_id(avatar_hash[3:])
        return Asset._from_application_asset(application_id, avatar_hash)
