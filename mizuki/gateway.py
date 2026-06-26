from __future__ import annotations

import sys
import asyncio
import aiohttp
import time
import json
import random
import logging

from typing import Any, TYPE_CHECKING

from mizuki.flags import IntentFlags
from mizuki.errors import GatewayError
from mizuki._event_dispatch import EventDispatcher

if TYPE_CHECKING:
    from mizuki.bot import Bot

_log = logging.getLogger(__name__)


class GatewayClient:
    """
    The Client that is used to connect and recieve events over gateway. This should **not** be constructed by the user.
    """

    token: str
    "The bot token used to authenticate with discord."

    intents: IntentFlags
    "The IntentFlags passed to the gateway."

    latency: float
    "The latency (in microseconds) for the gateway connection."

    __slots__ = (
        "token",
        "intents",
        "latency",
        "_dispatcher",
        "_ws",
        "_sequence",
        "_resume_ws_url",
        "_session_id",
        "_last_ack",
        "_heartbeat_interval",
        "_heartbeat_task",
        "_heartbeat_sent_at",
        "_listen_task",
        "_session",
        "_closed",
        "_reconnect_lock",
        "_handlers",
    )

    _URL = "wss://gateway.discord.gg/?v=10&encoding=json"
    _RECONNECTABLE_CLOSE_CODES = [4000, 4001, 4002, 4003, 4005, 4007, 4008, 4009]

    _GATEWAY_CODE_MESSAGES = {
        4000: "Unknown error: We're not sure what went wrong. Try reconnecting?",
        4001: "Unkown opcode: You sent an invalid Gateway opcode or an invalid payload for an opcode. Don't do that!",
        4002: "Decode error: You sent an invalid payload to Discord. Don't do that!",
        4003: "Not authenticated: You sent us a payload prior to identifying, or this session has been invalidated.",
        4004: "Authentication failed: The account token sent with your identify payload is incorrect.",
        4005: "Already authenticated: You sent more than one identify payload. Don't do that!",
        4007: "Invalid seq: The sequence sent when resuming the session was invalid. Reconnect and start a new session.",
        4008: "Rate limited: Woah nelly! You're sending payloads to us too quickly. Slow it down! You will be disconnected on receiving this.",
        4009: "Session timed out: Your session timed out. Reconnect and start a new one.",
        4010: "Invalid shard: You sent us an invalid shard when identifying.",
        4011: "Sharding required: The session would have handled too many guilds - you are required to shard your connection in order to connect.",
        4012: "Invalid API version: You sent an invalid version for the gateway.",
        4013: "Invalid intents: You sent an invalid intent for a Gateway Intent. You may have incorrectly calculated the bitwise value.",
        4014: "Disallowed intents: You sent a disallowed intent for a Gateway Intent. You may have tried to specify an intent that you have not enabled or are not approved for.",
    }

    def __init__(
        self, bot: Bot, session: aiohttp.ClientSession, token: str, intents: IntentFlags
    ):
        self.token = token
        self.intents = intents
        self.latency = 0.0

        self._dispatcher = EventDispatcher(bot)
        self._session = session
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._sequence: int | None = None
        self._resume_ws_url: str | None = None
        self._session_id: str | None = None
        self._last_ack: bool = True
        self._heartbeat_interval: float | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._heartbeat_sent_at: float = 0.0
        self._listen_task: asyncio.Task | None = None
        self._closed = asyncio.Event()
        self._reconnect_lock = asyncio.Lock()

        self._handlers = {
            0: self._handle_dispatch,
            1: self._handle_immediate_heartbeat,
            7: self._handle_reconnect,
            9: self._handle_invalid_session,
            10: self._handle_hello,
            11: self._handle_heartbeat_ack,
        }

    async def _send(self, data: dict[str, Any]):
        assert self._ws is not None, "Attempted to use websocket without connecting."
        await self._ws.send_json(data)

    async def _send_heartbeat(self):
        await self._send({"op": 1, "d": self._sequence})

    async def connect(self, resume_url: str | None = None):
        """
        Used to connect and start listening to the gateway events.

        Parameters
        ----------
        resume_url : :class:`str` | :class:`None`, optional
            The URL to resume the gateway connection with, if any. Defaults to ``None``
        """
        self._ws = await self._session.ws_connect(resume_url or self._URL)
        if resume_url is None:
            _log.info("Connected to discord gateway.")
        else:
            _log.info("Resumed Gateway Connection with resume_url: %s", resume_url)
        self._listen_task = asyncio.create_task(self._listen())
        self._listen_task.add_done_callback(self._on_task_done)

    def _on_task_done(self, task: asyncio.Task):
        if task.cancelled():
            return
        if task.exception() is not None:
            self._closed.set()

    async def wait_until_closed(self):
        """
        Waits until the gateway connection is closed.

        This coroutine blocks until the gateway disconnects. Useful for keeping the bot alive in a main coroutine.
        """
        await self._closed.wait()

    async def close(self):
        """
        Closes and cleans up the gateway connection.
        """
        self._closed.set()

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self._ws:
            await self._ws.close()

        if self._listen_task:
            await self._listen_task

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

            _log.debug(
                "Received Gateway Payload: Opcode = %s, Data Size = %s bytes, Sequence = %s, Event = %s",
                op,
                len(msg.data),
                sequence,
                event,
            )

            if sequence is not None:
                self._sequence = sequence

            handler = self._handlers.get(op)
            if handler:
                await handler(data, event)

        close_code = self._ws.close_code
        if close_code in self._RECONNECTABLE_CLOSE_CODES or close_code is None:
            _log.error(
                "Gateway Connection was disconnected, Attempting to reconnect. (Error Code = %s)",
                close_code,
            )
            await self._handle_reconnect()
        else:
            self._closed.set()
            raise GatewayError(
                close_code, self._GATEWAY_CODE_MESSAGES.get(close_code, "")
            )

    async def _heartbeat_loop(self):
        if self._heartbeat_interval:
            await asyncio.sleep(self._heartbeat_interval * random.random())
        while True:
            if not self._ws:
                return
            if not self._last_ack:
                _log.info(
                    "Did not receive any HEARTBEAT ACK for the last heartbeat sent. Detected Zombied Connection and Closing Gateway connection."
                )
                return await self._ws.close(code=4000)

            self._last_ack = False
            self._heartbeat_sent_at = time.monotonic()
            await self._send_heartbeat()

            if not self._heartbeat_interval:
                return
            await asyncio.sleep(self._heartbeat_interval)

    async def _handle_heartbeat_ack(self, *_):
        self.latency = time.monotonic() - self._heartbeat_sent_at
        _log.debug(
            "Received HEARTBEAT ACK (Opcode = 11) with latency %.2fms",
            self.latency * 1000,
        )
        self._last_ack = True

    async def _handle_immediate_heartbeat(self, *_):
        await self._send_heartbeat()

    async def _handle_hello(self, data: dict[str, Any], _):
        self._heartbeat_interval = data["heartbeat_interval"] / 1000
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        if self._session_id:
            await self._send(
                {
                    "op": 6,
                    "d": {
                        "token": self.token,
                        "session_id": self._session_id,
                        "seq": self._sequence,
                    },
                }
            )
            _log.debug(
                "Sent RESUME (Opcode = 6) to Discord Gateway (Session ID = %s)",
                self._session_id,
            )
        else:
            await self._send(
                {
                    "op": 2,
                    "d": {
                        "token": self.token,
                        "intents": int(self.intents),
                        "properties": {
                            "os": sys.platform,
                            "browser": "mizuki",
                            "device": "mizuki",
                        },
                    },
                }
            )
            _log.debug("Sent IDENTIFY (Opcode = 2) to Discord Gateway.")

    async def _handle_reconnect(self, *_):
        if self._reconnect_lock.locked():
            return
        asyncio.create_task(self._reconnect())

    async def _reconnect(self, *_):
        async with self._reconnect_lock:
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                self._heartbeat_interval = None

            if self._ws:
                await self._ws.close(code=4000)
                self._ws = None

            if self._listen_task:
                await self._listen_task
                self._listen_task = None

            await self.connect(self._resume_ws_url)

    async def _handle_ready(self, data: dict[str, Any]):
        # for now
        self._resume_ws_url = data["resume_gateway_url"] + "/?v=10&encoding=json"
        self._session_id = data["session_id"]

    async def _handle_invalid_session(self, data: bool, _):
        if data is False:
            self._session_id = None
            self._sequence = None
            self._resume_ws_url = None

        _log.info(
            "Gateway Session was invalidated. Closing Gateway Connection now. (Resumable = %s)",
            data,
        )
        if self._ws:
            await self._ws.close(code=4000)

    async def _handle_dispatch(self, data: dict[str, Any], event: str):
        if event == "READY":
            await self._handle_ready(data)
        h = self._dispatcher._dispatch_handlers.get(event)
        if h is not None:
            await h(data)
        else:
            _log.debug("No handler registered for event %s", event)
