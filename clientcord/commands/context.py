from typing import Any
from ..models.guild import Guild
from ..models.channel import Channel
from ..models.user import User
from ..models.member import Member

class Context:
    __slots__ = ("client", "_interaction", "_message", "options", "user", "guild", "channel", "member", "deferred", "responded")
    def __init__(self, client: Any, interaction: dict | None = None, message: dict | None = None) -> None:
        self.client = client
        self._interaction = interaction
        self._message = message
        self.options: dict[str, Any] = {}

    @property
    def interaction(self) -> dict | None:
        return self._interaction

    @property
    def message(self) -> dict | None:
        return self._message
        
        self.user = None
        self.guild = None
        self.channel = None
        self.member = None
        
        self.deferred = False
        self.responded = False
        
        payload = interaction or message
        if payload:
            if "guild_id" in payload:
                self.guild = Guild(id=payload["guild_id"])
                self.guild._client = client
            if "channel_id" in payload:
                self.channel = Channel(id=payload["channel_id"])
                self.channel._client = client
                
            author_data = payload.get("author") or (payload.get("member", {}).get("user")) or payload.get("user")
            if author_data:
                self.user = User(id=author_data["id"])
                self.user._client = client
                
            member_data = payload.get("member")
            if member_data and "guild_id" in payload:
                self.member = Member(guild_id=payload["guild_id"])
                self.member._client = client
                if self.user:
                    self.member.user = self.user

    async def write(self, content: str = "", **kwargs) -> None:
        if "components" in kwargs and isinstance(kwargs["components"], list):
            new_components = []
            for c in kwargs["components"]:
                if isinstance(c, dict):
                    new_components.append(c)
                elif hasattr(c, "to_dict"):
                    new_components.append(c.to_dict())
                else:
                    new_components.append(c)
            kwargs["components"] = new_components
            
        if self._interaction:
            if self.deferred:
                endpoint = f"/webhooks/{self.client.application_id}/{self._interaction['token']}/messages/@original"
                await self.client.http.request("PATCH", endpoint, "webhook", json={"content": content, **kwargs})
            else:
                endpoint = f"/interactions/{self._interaction['id']}/{self._interaction['token']}/callback"
                await self.client.http.request("POST", endpoint, "interaction", json={"type": 4, "data": {"content": content, **kwargs}})
                self.responded = True
        elif self._message:
            await self.client.http.send_message(self._message["channel_id"], content, **kwargs)

    async def defer(self, ephemeral: bool = False) -> None:
        if self._interaction and not self.responded:
            flags = 64 if ephemeral else 0
            endpoint = f"/interactions/{self._interaction['id']}/{self._interaction['token']}/callback"
            await self.client.http.request("POST", endpoint, "interaction", json={"type": 5, "data": {"flags": flags}})
            self.deferred = True
            self.responded = True

    async def edit(self, content: str) -> None:
        if self._interaction:
            endpoint = f"/webhooks/{self.client.application_id}/{self._interaction['token']}/messages/@original"
            await self.client.http.request("PATCH", endpoint, "webhook", json={"content": content})

    async def show_modal(self, modal: Any) -> None:
        if self._interaction and not self.responded:
            data = modal.to_dict() if hasattr(modal, "to_dict") else modal
            if "components" in data:
                new_comps = []
                for row in data["components"]:
                    if hasattr(row, "to_dict"):
                        new_comps.append(row.to_dict())
                    else:
                        new_comps.append(row)
                data["components"] = new_comps

            endpoint = f"/interactions/{self._interaction['id']}/{self._interaction['token']}/callback"
            await self.client.http.request("POST", endpoint, "interaction", json={"type": 9, "data": data})
            self.responded = True
