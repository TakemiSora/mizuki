from __future__ import annotations

class Asset:
    CDN_URL = "https://cdn.discordapp.com"

    def __init__(self, url: str, animated: bool):
        self.url = url
        self.animated = animated

    @classmethod
    def _from_user_avatar(cls, user_id: int, avatar_hash: str | None) -> Asset | None:
        if avatar_hash is not None:
            is_animated = avatar_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/avatars/{user_id}/{avatar_hash}.webp{"?animated=true" if is_animated else ""}",
                is_animated
            )
        return None

    @classmethod
    def _from_user_banner(cls, user_id: int, banner_hash: str | None) -> Asset | None:
        if banner_hash is not None:
            is_animated = banner_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/banners/{user_id}/{banner_hash}.webp{"?animated=true" if is_animated else ""}",
                is_animated
            )
        return None

    @classmethod
    def _from_user_avatar_decoration(cls, avatar_decoration_hash: str) -> Asset:
        is_animated = avatar_decoration_hash.startswith("a_")
        return cls(
            f"{cls.CDN_URL}/avatar-decoration-presets/{avatar_decoration_hash}.png",
            is_animated
        )

    @classmethod
    def _from_collectibles_nameplate(cls, nameplate_asset: str) -> Asset:
        return cls(
            f"{cls.CDN_URL}/assets/collectibles/{nameplate_asset}asset.webm",
            True
        )

    @classmethod
    def _from_guild_avatar(cls, guild_id: int, avatar_hash: str | None) -> Asset | None:
        if avatar_hash is not None:
            is_animated = avatar_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/icons/{guild_id}/{avatar_hash}.webp{"?animated=true" if is_animated else ""}",
                is_animated
            )
        return None

    @classmethod
    def _from_guild_splash(cls, guild_id: int, splash_hash: str | None) -> Asset | None:
        if splash_hash is not None:
            return cls(
                f"{cls.CDN_URL}/splashes/{guild_id}/{splash_hash}.webp",
                False
            )
        return None

    @classmethod
    def _from_guild_discovery_splash(cls, guild_id: int, splash_hash: str | None) -> Asset | None:
        if splash_hash is not None:
            return cls(
                f"{cls.CDN_URL}/discovery-splashes/{guild_id}/{splash_hash}.webp",
                False
            )
        return None
    
    @classmethod
    def _from_guild_tag_badge(cls, guild_id: int | None, badge_hash: str | None) -> Asset | None:
        if guild_id is not None and badge_hash is not None:
            return cls(
                f"{cls.CDN_URL}/guild-tag-badges/{guild_id}/{badge_hash}.webp",
                False
            )
        return None
        
    @classmethod
    def _from_role_icon(cls, role_id: int, role_hash: str | None) -> Asset | None:
        if role_hash is not None:
            return cls(
                f"{cls.CDN_URL}/role-icons/{role_id}/{role_hash}.webp",
                False
            )
        return None