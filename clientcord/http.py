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
        
        headers = {**self.headers, **kwargs.pop("headers", {})}
        
        while True:
            response = await self.client.request(url, method, headers=headers, **kwargs)
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

    async def send_message(self, channel_id: str, content: str = "", **kwargs) -> dict:
        if "components" in kwargs and kwargs["components"]:
            kwargs["flags"] = kwargs.get("flags", 0) | 32768
            if content:
                kwargs["components"].insert(0, {"type": 10, "content": content})
                content = ""
            kwargs.pop("embeds", None)
            
        payload = {"content": content, **kwargs} if content else kwargs
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/channels/{channel_id}/messages", f"channel:{channel_id}", data=data)

    async def edit_message(self, channel_id: str, message_id: str, content: str = "", **kwargs) -> dict:
        if "components" in kwargs and kwargs["components"]:
            kwargs["flags"] = kwargs.get("flags", 0) | 32768
            if content:
                kwargs["components"].insert(0, {"type": 10, "content": content})
                content = ""
            kwargs.pop("embeds", None)
            
        payload = {"content": content, **kwargs} if content else kwargs
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/channels/{channel_id}/messages/{message_id}", f"channel:{channel_id}", data=data)

    async def delete_message(self, channel_id: str, message_id: str) -> None:
        await self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}", f"channel:{channel_id}")

    async def get_guild(self, guild_id: str) -> dict:
        return await self.request("GET", f"/guilds/{guild_id}", f"guild:{guild_id}")

    async def get_channel(self, channel_id: str) -> dict:
        return await self.request("GET", f"/channels/{channel_id}", f"channel:{channel_id}")

    async def modify_channel(self, channel_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/channels/{channel_id}", f"channel:{channel_id}", data=data, headers=headers)

    async def delete_channel(self, channel_id: str, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("DELETE", f"/channels/{channel_id}", f"channel:{channel_id}", headers=headers)

    async def create_guild_channel(self, guild_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/guilds/{guild_id}/channels", f"guild:{guild_id}", data=data, headers=headers)

    async def edit_channel_permissions(self, channel_id: str, overwrite_id: str, payload: dict, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        await self.request("PUT", f"/channels/{channel_id}/permissions/{overwrite_id}", f"channel:{channel_id}", data=data, headers=headers)

    async def delete_channel_permission(self, channel_id: str, overwrite_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("DELETE", f"/channels/{channel_id}/permissions/{overwrite_id}", f"channel:{channel_id}", headers=headers)

    async def get_channel_invites(self, channel_id: str) -> list[dict]:
        return await self.request("GET", f"/channels/{channel_id}/invites", f"channel:{channel_id}")

    async def create_channel_invite(self, channel_id: str, payload: dict | None = None, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload or {})
        return await self.request("POST", f"/channels/{channel_id}/invites", f"channel:{channel_id}", data=data, headers=headers)

    async def follow_announcement_channel(self, channel_id: str, webhook_channel_id: str, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode({"webhook_channel_id": webhook_channel_id})
        return await self.request("POST", f"/channels/{channel_id}/followers", f"channel:{channel_id}", data=data, headers=headers)

    async def trigger_typing(self, channel_id: str) -> None:
        await self.request("POST", f"/channels/{channel_id}/typing", f"channel:{channel_id}")

    async def start_thread_from_message(self, channel_id: str, message_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/channels/{channel_id}/messages/{message_id}/threads", f"channel:{channel_id}", data=data, headers=headers)

    async def start_thread(self, channel_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/channels/{channel_id}/threads", f"channel:{channel_id}", data=data, headers=headers)

    async def join_thread(self, channel_id: str) -> None:
        await self.request("PUT", f"/channels/{channel_id}/thread-members/@me", f"channel:{channel_id}")

    async def leave_thread(self, channel_id: str) -> None:
        await self.request("DELETE", f"/channels/{channel_id}/thread-members/@me", f"channel:{channel_id}")

    async def add_thread_member(self, channel_id: str, user_id: str) -> None:
        await self.request("PUT", f"/channels/{channel_id}/thread-members/{user_id}", f"channel:{channel_id}")

    async def remove_thread_member(self, channel_id: str, user_id: str) -> None:
        await self.request("DELETE", f"/channels/{channel_id}/thread-members/{user_id}", f"channel:{channel_id}")

    async def get_thread_member(self, channel_id: str, user_id: str, with_member: bool = False) -> dict:
        params = f"?with_member=true" if with_member else ""
        return await self.request("GET", f"/channels/{channel_id}/thread-members/{user_id}{params}", f"channel:{channel_id}")

    async def list_thread_members(self, channel_id: str, with_member: bool = False, after: str | None = None, limit: int = 100) -> list[dict]:
        params = []
        if with_member:
            params.append("with_member=true")
        if after:
            params.append(f"after={after}")
        if limit != 100:
            params.append(f"limit={limit}")
        qs = f"?{'&'.join(params)}" if params else ""
        return await self.request("GET", f"/channels/{channel_id}/thread-members{qs}", f"channel:{channel_id}")

    async def list_public_archived_threads(self, channel_id: str, before: str | None = None, limit: int | None = None) -> dict:
        params = []
        if before:
            params.append(f"before={before}")
        if limit:
            params.append(f"limit={limit}")
        qs = f"?{'&'.join(params)}" if params else ""
        return await self.request("GET", f"/channels/{channel_id}/threads/archived/public{qs}", f"channel:{channel_id}")

    async def list_private_archived_threads(self, channel_id: str, before: str | None = None, limit: int | None = None) -> dict:
        params = []
        if before:
            params.append(f"before={before}")
        if limit:
            params.append(f"limit={limit}")
        qs = f"?{'&'.join(params)}" if params else ""
        return await self.request("GET", f"/channels/{channel_id}/threads/archived/private{qs}", f"channel:{channel_id}")

    async def list_joined_private_archived_threads(self, channel_id: str, before: str | None = None, limit: int | None = None) -> dict:
        params = []
        if before:
            params.append(f"before={before}")
        if limit:
            params.append(f"limit={limit}")
        qs = f"?{'&'.join(params)}" if params else ""
        return await self.request("GET", f"/channels/{channel_id}/users/@me/threads/archived/private{qs}", f"channel:{channel_id}")

    async def get_guild_audit_log(self, guild_id: str, user_id: str | None = None, action_type: int | None = None, before: str | None = None, after: str | None = None, limit: int = 50) -> dict:
        params = []
        if user_id:
            params.append(f"user_id={user_id}")
        if action_type is not None:
            params.append(f"action_type={action_type}")
        if before:
            params.append(f"before={before}")
        if after:
            params.append(f"after={after}")
        if limit != 50:
            params.append(f"limit={limit}")
        qs = f"?{'&'.join(params)}" if params else ""
        return await self.request("GET", f"/guilds/{guild_id}/audit-logs{qs}", f"guild:{guild_id}")

    async def list_auto_moderation_rules(self, guild_id: str) -> list[dict]:
        return await self.request("GET", f"/guilds/{guild_id}/auto-moderation/rules", f"guild:{guild_id}")

    async def get_auto_moderation_rule(self, guild_id: str, rule_id: str) -> dict:
        return await self.request("GET", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}", f"guild:{guild_id}")

    async def create_auto_moderation_rule(self, guild_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/guilds/{guild_id}/auto-moderation/rules", f"guild:{guild_id}", data=data, headers=headers)

    async def modify_auto_moderation_rule(self, guild_id: str, rule_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}", f"guild:{guild_id}", data=data, headers=headers)

    async def delete_auto_moderation_rule(self, guild_id: str, rule_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("DELETE", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}", f"guild:{guild_id}", headers=headers)

    async def list_guild_emojis(self, guild_id: str) -> list[dict]:
        return await self.request("GET", f"/guilds/{guild_id}/emojis", f"guild:{guild_id}")

    async def get_guild_emoji(self, guild_id: str, emoji_id: str) -> dict:
        return await self.request("GET", f"/guilds/{guild_id}/emojis/{emoji_id}", f"guild:{guild_id}")

    async def create_guild_emoji(self, guild_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/guilds/{guild_id}/emojis", f"guild:{guild_id}", data=data, headers=headers)

    async def modify_guild_emoji(self, guild_id: str, emoji_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/guilds/{guild_id}/emojis/{emoji_id}", f"guild:{guild_id}", data=data, headers=headers)

    async def delete_guild_emoji(self, guild_id: str, emoji_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("DELETE", f"/guilds/{guild_id}/emojis/{emoji_id}", f"guild:{guild_id}", headers=headers)

    async def list_application_emojis(self, application_id: str) -> dict:
        return await self.request("GET", f"/applications/{application_id}/emojis", f"app:{application_id}")

    async def get_application_emoji(self, application_id: str, emoji_id: str) -> dict:
        return await self.request("GET", f"/applications/{application_id}/emojis/{emoji_id}", f"app:{application_id}")

    async def add_guild_member_role(self, guild_id: str, user_id: str, role_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("PUT", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", f"guild:{guild_id}", headers=headers)

    async def remove_guild_member_role(self, guild_id: str, user_id: str, role_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("DELETE", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", f"guild:{guild_id}", headers=headers)

    async def get_guild_roles(self, guild_id: str) -> list[dict]:
        return await self.request("GET", f"/guilds/{guild_id}/roles", f"guild:{guild_id}")

    async def create_guild_role(self, guild_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/guilds/{guild_id}/roles", f"guild:{guild_id}", data=data, headers=headers)

    async def create_guild_ban(self, guild_id: str, user_id: str, delete_message_seconds: int = 0, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode({"delete_message_seconds": delete_message_seconds})
        await self.request("PUT", f"/guilds/{guild_id}/bans/{user_id}", f"guild:{guild_id}", data=data, headers=headers)

    async def remove_guild_ban(self, guild_id: str, user_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("DELETE", f"/guilds/{guild_id}/bans/{user_id}", f"guild:{guild_id}", headers=headers)

    async def remove_guild_member(self, guild_id: str, user_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("DELETE", f"/guilds/{guild_id}/members/{user_id}", f"guild:{guild_id}", headers=headers)

    async def get_global_application_commands(self, application_id: str) -> list[dict]:
        return await self.request("GET", f"/applications/{application_id}/commands", "global")

    async def create_global_application_command(self, application_id: str, payload: dict) -> dict:
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/applications/{application_id}/commands", "global", data=data)

    async def edit_global_application_command(self, application_id: str, command_id: str, payload: dict) -> dict:
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/applications/{application_id}/commands/{command_id}", "global", data=data)

    async def delete_global_application_command(self, application_id: str, command_id: str) -> None:
        await self.request("DELETE", f"/applications/{application_id}/commands/{command_id}", "global")

    async def bulk_overwrite_global_application_commands(self, application_id: str, payload: list[dict]) -> list[dict]:
        data = msgspec.json.encode(payload)
        return await self.request("PUT", f"/applications/{application_id}/commands", "global", data=data)

    async def get_guild_application_commands(self, application_id: str, guild_id: str) -> list[dict]:
        return await self.request("GET", f"/applications/{application_id}/guilds/{guild_id}/commands", f"guild:{guild_id}")

    async def create_guild_application_command(self, application_id: str, guild_id: str, payload: dict) -> dict:
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/applications/{application_id}/guilds/{guild_id}/commands", f"guild:{guild_id}", data=data)

    async def edit_guild_application_command(self, application_id: str, guild_id: str, command_id: str, payload: dict) -> dict:
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}", f"guild:{guild_id}", data=data)

    async def delete_guild_application_command(self, application_id: str, guild_id: str, command_id: str) -> None:
        await self.request("DELETE", f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}", f"guild:{guild_id}")

    async def bulk_overwrite_guild_application_commands(self, application_id: str, guild_id: str, payload: list[dict]) -> list[dict]:
        data = msgspec.json.encode(payload)
        return await self.request("PUT", f"/applications/{application_id}/guilds/{guild_id}/commands", f"guild:{guild_id}", data=data)

    async def execute_webhook(self, webhook_id: str, webhook_token: str | None, content: str = "", **kwargs) -> dict | None:
        wait = kwargs.pop("wait", False)
        if "components" in kwargs and kwargs["components"]:
            kwargs["flags"] = kwargs.get("flags", 0) | 32768
            if content:
                kwargs["components"].insert(0, {"type": 10, "content": content})
                content = ""
            kwargs.pop("embeds", None)
            
        payload = {"content": content, **kwargs} if content else kwargs
        data = msgspec.json.encode(payload)
        url = f"/webhooks/{webhook_id}/{webhook_token}" if webhook_token else f"/webhooks/{webhook_id}"
        qs = "?wait=true" if wait else ""
        return await self.request("POST", f"{url}{qs}", f"webhook:{webhook_id}", data=data)

    async def modify_webhook(self, webhook_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/webhooks/{webhook_id}", f"webhook:{webhook_id}", data=data, headers=headers)

    async def modify_webhook_with_token(self, webhook_id: str, webhook_token: str, payload: dict) -> dict:
        data = msgspec.json.encode(payload)
        return await self.request("PATCH", f"/webhooks/{webhook_id}/{webhook_token}", f"webhook:{webhook_id}", data=data)

    async def delete_webhook(self, webhook_id: str, reason: str | None = None) -> None:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        await self.request("DELETE", f"/webhooks/{webhook_id}", f"webhook:{webhook_id}", headers=headers)

    async def create_webhook(self, channel_id: str, payload: dict, reason: str | None = None) -> dict:
        headers = {**self.headers}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        data = msgspec.json.encode(payload)
        return await self.request("POST", f"/channels/{channel_id}/webhooks", f"channel:{channel_id}", data=data, headers=headers)

    async def delete_webhook_with_token(self, webhook_id: str, webhook_token: str) -> None:
        await self.request("DELETE", f"/webhooks/{webhook_id}/{webhook_token}", f"webhook:{webhook_id}")
