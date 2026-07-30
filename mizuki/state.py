from __future__ import annotations
from collections.abc import Coroutine, Callable, Sequence
import aiohttp

from typing import TYPE_CHECKING, Any

from mizuki.flags import IntentFlags
from mizuki.http import HTTPClient
from mizuki.gateway import GatewayClient
from mizuki.managers.resource import Managers

if TYPE_CHECKING:
    from mizuki.bot import Bot
    from mizuki.cache import CacheStorage
    from mizuki.objects.command import PartialApplicationCommand
    from mizuki.objects.components import Component
    from mizuki.objects.interaction import Interaction
    from mizuki.objects.modal import Modal, ModalResponse


class ConnectionState:
    __slots__ = (
        "http",
        "gateway",
        "managers",
        "session",
        "components_data",
        "modals_data",
    )

    def __init__(self):
        self.components_data: dict[
            tuple[int, str], Callable[[Interaction, Any], Coroutine[Any, Any, Any]]
        ] = {}

        self.modals_data: dict[
            str,
            Callable[[Interaction, ModalResponse], Coroutine[Any, Any, Any]],
        ] = {}

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
        commands_data: dict[str, tuple[int, PartialApplicationCommand]],
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

    def register_components(
        self, message_id: int, components: Sequence[Component]
    ) -> None:
        for component in components:
            if (custom_id := getattr(component, "custom_id", None)) and (
                callback := getattr(component, "_callback", None)
            ):
                self.components_data[message_id, custom_id] = callback

            if child_components := getattr(component, "components", ()):
                self.register_components(message_id, child_components)

    def register_modal(self, modal: Modal) -> None:
        if callback := getattr(modal, "_callback", None):
            self.modals_data[modal.custom_id] = callback
