import aiosonic
import msgspec
import asyncio
from typing import Any
from .ratelimits import RateLimiter
from .errors import HTTPError

class HTTPClient:
    def __init__(self, token: str) -> None:
        self.token = token
        self.client = aiosonic.HTTPClient()
        self.ratelimiter = RateLimiter()
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }

    async def request(self, method: str, route: str, bucket: str, **kwargs) -> Any:
        url = self.base_url + route
        await self.ratelimiter.acquire(bucket)
        
        while True:
            response = await self.client.request(url, method, headers=self.headers, **kwargs)
            body_bytes = await response.content()
            
            remaining = int(response.headers.get("X-RateLimit-Remaining", "1"))
            reset = float(response.headers.get("X-RateLimit-Reset", "0.0"))
            is_global = response.headers.get("X-RateLimit-Global", "false") == "true"
            
            if response.status_code == 429:
                body = msgspec.json.decode(body_bytes)
                retry_after = float(body.get("retry_after", 0.0))
                self.ratelimiter.update(bucket, 0, 0.0, is_global, retry_after)
                await asyncio.sleep(retry_after)
                continue
                
            self.ratelimiter.update(bucket, remaining, reset)
            
            if not (200 <= response.status_code < 300):
                raise HTTPError(response.status_code, body_bytes.decode("utf-8"))
                
            if response.status_code == 204:
                return None
                
            return msgspec.json.decode(body_bytes)

    async def send_message(self, channel_id: str, content: str) -> dict:
        data = msgspec.json.encode({"content": content})
        return await self.request("POST", f"/channels/{channel_id}/messages", f"channel:{channel_id}", data=data)

    async def edit_message(self, channel_id: str, message_id: str, content: str) -> dict:
        data = msgspec.json.encode({"content": content})
        return await self.request("PATCH", f"/channels/{channel_id}/messages/{message_id}", f"channel:{channel_id}", data=data)

    async def delete_message(self, channel_id: str, message_id: str) -> None:
        await self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}", f"channel:{channel_id}")

    async def get_guild(self, guild_id: str) -> dict:
        return await self.request("GET", f"/guilds/{guild_id}", f"guild:{guild_id}")

    async def get_channel(self, channel_id: str) -> dict:
        return await self.request("GET", f"/channels/{channel_id}", f"channel:{channel_id}")
