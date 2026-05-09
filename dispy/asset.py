from __future__ import annotations
from .state import State

class Asset:
    CDN_URL = "https://cdn.discordapp.com"

    def __init__(self, url: str, state: State, animated: bool):
        self.url = url
        self._state = state
        self.animated = animated

    @classmethod
    def _from_user_avatar(cls, state: State, user_id: int, avatar_hash: str | None) -> Asset | None:
        if avatar_hash is not None:
            is_animated = avatar_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/avatars/{user_id}/{avatar_hash}.webp{"?animated=true" if is_animated else ""}",
                state, is_animated
            )
        return None

    @classmethod
    def _from_user_banner(cls, state: State, user_id: int, banner_hash: str | None) -> Asset | None:
        if banner_hash is not None:
            is_animated = banner_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/banners/{user_id}/{banner_hash}.webp{"?animated=true" if is_animated else ""}",
                state, is_animated
            )
        return None

    @classmethod
    def _from_user_avatar_decoration(cls, state: State, avatar_decoration_hash: str | None) -> Asset | None:
        if avatar_decoration_hash is not None:
            is_animated = avatar_decoration_hash.startswith("a_")
            return cls(
                f"{cls.CDN_URL}/avatar-decoration-presets/{avatar_decoration_hash}.webp{"?animated=true" if is_animated else ""}",
                state, is_animated
            )
        return None
