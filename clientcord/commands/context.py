from typing import Any

class Context:
    def __init__(self, client: Any, interaction: dict | None = None, message: dict | None = None) -> None:
        self.client = client
        self._interaction = interaction
        self._message = message
        self.options: dict[str, Any] = {}
        
        self.user = None
        self.guild = None
        self.channel = None
        
        self.deferred = False
        self.responded = False

    async def write(self, content: str) -> None:
        if self._interaction:
            if self.deferred:
                endpoint = f"/webhooks/{self.client.application_id}/{self._interaction['token']}/messages/@original"
                await self.client.http.request("PATCH", endpoint, "webhook", json={"content": content})
            else:
                endpoint = f"/interactions/{self._interaction['id']}/{self._interaction['token']}/callback"
                await self.client.http.request("POST", endpoint, "interaction", json={"type": 4, "data": {"content": content}})
                self.responded = True
        elif self._message:
            await self.client.http.send_message(self._message["channel_id"], content)

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
