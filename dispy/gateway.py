import sys
import asyncio
import aiohttp
import json
from typing import Any
from .flags import IntentFlags

class GatewayClient:
    __slots__ = (
        "token",
        "intents",
        "_ws",
        "_sequence",
        "_last_ack",
        "_heartbeat_interval",
        "_heartbeat_task",
        "_listen_task",
        "_session",
        "_handlers"
    )
    
    URL = "wss://gateway.discord.gg/?v=10&encoding=json"

    def __init__(self, token: str, intents: IntentFlags):
        self.token = token
        self.intents = intents

        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._sequence: int | None = None
        self._last_ack: bool = True
        self._heartbeat_interval: float | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._listen_task: asyncio.Task | None = None
        self._session: aiohttp.ClientSession | None = None

        self._handlers = {
            0: self._handle_dispatch,
            10: self._handle_hello,
            11: self._handle_heartbeat_ack
        }

    async def _send(self, data: dict[str, Any]):
        assert self._ws is not None, "Attempted to use websocket without connecting."
        await self._ws.send_json(data)

    async def connect(self):
        self._session = aiohttp.ClientSession()
        self._ws = await self._session.ws_connect(self.URL)
        self._listen_task = asyncio.create_task(self._listen())

    async def wait_until_closed(self):
        if self._listen_task:
            await self._listen_task

    async def close(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self._ws:
            await self._ws.close()
            
        if self._session:
            await self._session.close()

    async def _listen(self):
        assert self._ws is not None, "Attempted to use websocket without connecting."
        async for msg in self._ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue

            payload = json.loads(msg.data)

            op = payload["op"]
            data = payload["d"]
            sequence = payload["s"]
            event = payload["t"]

            if sequence is not None:
                self._sequence = sequence

            handler = self._handlers.get(op)
            if handler:
                await handler(data, event)

    async def _heartbeat_loop(self):
        while True:
            if not self._last_ack:
                assert self._ws is not None, "Attempted to use websocket without connecting."
                return await self._ws.close()
            self._last_ack = False

            await self._send({
                "op": 1,
                "d": self._sequence
            })
            
            assert self._heartbeat_interval is not None, "Attempted to use heartbeat without connecting."
            await asyncio.sleep(self._heartbeat_interval)

    async def _handle_heartbeat_ack(self, _, __):
        self._last_ack = True

    async def _handle_hello(self, data: dict[str, Any], _):
        self._heartbeat_interval = data["heartbeat_interval"] / 1000
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        await self._send({
            "op": 2,
            "d": {
                "token": self.token,
                "intents": int(self.intents),
                "properties": {
                    "os": sys.platform,
                    "browser": "dispy",
                    "device": "dispy"
                },
            }
        })

    async def _handle_dispatch(self, data: dict[str, Any], event: str):
        print(event, data)