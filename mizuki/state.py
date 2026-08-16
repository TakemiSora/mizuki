from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Sequence
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import aiohttp

from mizuki.flags import IntentFlags
from mizuki.gateway import GatewayClient
from mizuki.http import HTTPClient
from mizuki.managers.resource import Managers

if TYPE_CHECKING:
    from mizuki.bot import Bot
    from mizuki.cache import CacheStorage
    from mizuki.objects.command import (
        PartialApplicationCommand,
        PartialApplicationCommandGroup,
    )
    from mizuki.objects.components import Component
    from mizuki.objects.interaction import Interaction
    from mizuki.objects.modal import Modal, ModalResponse


class ConnectionState:
    __slots__ = (
        "components_data",
        "default_component_timeout",
        "default_modal_timeout",
        "gateway",
        "http",
        "managers",
        "modals_data",
        "session",
    )

    def __init__(
        self,
        *,
        default_component_timeout: timedelta | None,
        default_modal_timeout: timedelta | None,
    ) -> None:
        self.components_data: dict[
            tuple[int, str],
            tuple[
                Callable[[Interaction, Any], Coroutine[Any, Any, Any]], datetime | None
            ],
        ] = {}

        self.modals_data: dict[
            str,
            tuple[
                Callable[[Interaction, ModalResponse], Coroutine[Any, Any, Any]],
                datetime | None,
            ],
        ] = {}

        self.default_component_timeout = default_component_timeout
        self.default_modal_timeout = default_modal_timeout

    def init_http(self, token: str) -> HTTPClient:
        self.http = HTTPClient(self)
        self.session = aiohttp.ClientSession(
            "https://discord.com/api/v10/", headers={"Authorization": f"Bot {token}"}
        )
        return self.http

    def init_managers(
        self,
        *,
        cache_storage: CacheStorage,
        application_id: int,
        commands_data: dict[
            str, tuple[int, PartialApplicationCommand | PartialApplicationCommandGroup]
        ],
    ) -> Managers:
        assert hasattr(self, "http"), "Init Manager was called without init http"
        self.managers = Managers(
            state=self,
            cache_storage=cache_storage,
            application_id=application_id,
            commands_data=commands_data,
        )
        return self.managers

    async def init_gateway(
        self, *, bot: Bot, token: str, intents: IntentFlags
    ) -> GatewayClient:
        assert hasattr(self, "http"), "Init Gateway was called without init http"
        self.gateway = GatewayClient(bot, self.session, token, intents)
        await self.gateway.connect()

        return self.gateway

    def start_cleanup_tasks(self) -> None:
        asyncio.create_task(self.cleanup_registered(self.components_data))
        asyncio.create_task(self.cleanup_registered(self.modals_data))

    async def cleanup_registered(
        self, data: dict[Any, tuple[Any, datetime | None]]
    ) -> None:
        while True:
            for key, (_, expires_at) in data.copy().items():
                if expires_at and expires_at < datetime.now(UTC):
                    data.pop(key)
            await asyncio.sleep(10)

    def register_components(
        self, message_id: int, components: Sequence[Component]
    ) -> None:
        for component in components:
            if (custom_id := getattr(component, "custom_id", None)) and (
                callback := getattr(component, "_callback", None)
            ):
                timeout: timedelta | None = getattr(
                    component, "_timeout", self.default_component_timeout
                )
                self.components_data[message_id, custom_id] = (
                    callback,
                    (datetime.now(UTC) + timeout) if timeout else None,
                )

            if child_components := getattr(component, "components", ()):
                self.register_components(message_id, child_components)

    def register_modal(self, modal: Modal) -> None:
        if callback := getattr(modal, "_callback", None):
            timeout: timedelta | None = getattr(
                modal, "_timeout", self.default_modal_timeout
            )
            self.modals_data[modal.custom_id] = (
                callback,
                (datetime.now(UTC) + timeout) if timeout else None,
            )
