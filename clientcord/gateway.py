import websockets
import asyncio
import msgspec
import sys
from .utils.compression import GatewayDecompressor
from .logger import info, debug, error, warn

class Gateway:
    def __init__(self, token: str, intents: int, dispatcher: "Dispatcher") -> None:
        self.token = token
        self.intents = intents
        self.dispatcher = dispatcher
        self.ws = None
        self.seq = None
        self.session_id = None
        self.resume_gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json&compress=zlib-stream"
        self.url = self.resume_gateway_url
        self.heartbeat_interval = 0
        self.heartbeat_task = None
        self.decompressor = GatewayDecompressor()
        self.closed = False

    async def connect(self) -> None:
        while not self.closed:
            try:
                self.decompressor = GatewayDecompressor()
                async with websockets.connect(self.url) as ws:
                    self.ws = ws
                    info("Gateway connected")
                    await self._receive_loop()
            except websockets.ConnectionClosed as e:
                warn(f"Gateway connection closed: {e.code} - {e.reason}")
                if e.code in (4004, 4010, 4011, 4012, 4013, 4014):
                    error("Fatal gateway close code. Exiting.")
                    break
                await asyncio.sleep(1)
            except Exception as e:
                error(f"Gateway exception: {e}")
                await asyncio.sleep(5)

    async def _receive_loop(self) -> None:
        async for msg in self.ws:
            if isinstance(msg, bytes):
                decompressed = self.decompressor.decompress(msg)
                if not decompressed:
                    continue
                data = msgspec.json.decode(decompressed)
            else:
                data = msgspec.json.decode(msg)
                
            asyncio.create_task(self._handle_payload(data))

    async def _handle_payload(self, payload: dict) -> None:
        op = payload.get("op")
        d = payload.get("d")
        s = payload.get("s")
        t = payload.get("t")

        if s is not None:
            self.seq = s

        if op == 10:
            self.heartbeat_interval = d["heartbeat_interval"] / 1000.0
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            self.heartbeat_task = asyncio.create_task(self._heartbeat())
            await self._identify_or_resume()

        elif op == 11:
            debug("Heartbeat acknowledged")

        elif op == 9:
            warn("Invalid session. Reconnecting.")
            if d:
                await self._resume()
            else:
                self.session_id = None
                self.seq = None
                await asyncio.sleep(2)
                await self._identify()

        elif op == 7:
            warn("Gateway requested reconnect")
            await self.ws.close(4000)

        elif op == 0:
            if t == "READY":
                self.session_id = d["session_id"]
                self.resume_gateway_url = d["resume_gateway_url"] + "?v=10&encoding=json&compress=zlib-stream"
                info(f"Session ready: {self.session_id}")
            
            await self.dispatcher.dispatch(t, d)

    async def _identify_or_resume(self) -> None:
        if self.session_id and self.seq:
            await self._resume()
        else:
            await self._identify()

    async def _identify(self) -> None:
        debug("Sending IDENTIFY")
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "os": sys.platform,
                    "browser": "clientcord",
                    "device": "clientcord"
                }
            }
        }
        if self.ws and not self.ws.closed:
            await self.ws.send(msgspec.json.encode(payload))

    async def _resume(self) -> None:
        debug("Sending RESUME")
        payload = {
            "op": 6,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.seq
            }
        }
        if self.ws and not self.ws.closed:
            await self.ws.send(msgspec.json.encode(payload))

    async def _heartbeat(self) -> None:
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            debug("Sending heartbeat")
            payload = {"op": 1, "d": self.seq}
            try:
                if self.ws and not self.ws.closed:
                    await self.ws.send(msgspec.json.encode(payload))
            except Exception:
                pass
