import msgspec
from .user import User
from .channel import Channel
from .guild import Guild
from .base import ClientObject

class Webhook(ClientObject):
    id: str
    type: int
    guild_id: str | None = None
    channel_id: str | None = None
    user: User | None = None
    name: str | None = None
    avatar: str | None = None
    token: str | None = None
    application_id: str | None = None
    source_guild: Guild | None = None
    source_channel: Channel | None = None
    url: str | None = None

    async def execute(self, content: str = "", **kwargs) -> dict | None:
        """Executes the webhook. If wait=True is passed in kwargs, returns the message dict."""
        if "components" in kwargs and isinstance(kwargs["components"], list):
            kwargs["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in kwargs["components"]]
        return await self.http.execute_webhook(self.id, self.token, content, **kwargs)

    async def edit(self, reason: str | None = None, **kwargs) -> dict:
        return await self.http.modify_webhook(self.id, kwargs, reason)

    async def edit_with_token(self, **kwargs) -> dict:
        return await self.http.modify_webhook_with_token(self.id, self.token, kwargs)

    async def delete(self, reason: str | None = None) -> None:
        await self.http.delete_webhook(self.id, reason)

    async def delete_with_token(self) -> None:
        await self.http.delete_webhook_with_token(self.id, self.token)
