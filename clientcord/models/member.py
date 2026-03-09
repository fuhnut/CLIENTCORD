import msgspec
from .user import User
from .base import ClientObject

class Member(ClientObject):
    roles: list[str] = []
    joined_at: str | None = None
    deaf: bool | None = None
    mute: bool | None = None
    user: User | None = None
    nick: str | None = None
    avatar: str | None = None
    premium_since: str | None = None
    flags: int = 0
    pending: bool = False
    permissions: str | None = None
    communication_disabled_until: str | None = None
    guild_id: str | None = None
    
    async def add_role(self, role_id: str, reason: str | None = None) -> None:
        if not self.guild_id or not self.user:
            raise ValueError("Member must be tied to a guild to add roles.")
            
        if not role_id.isdigit():
            roles = await self.http.get_guild_roles(self.guild_id)
            for r in roles:
                if r.get("name", "").lower() == role_id.lower():
                    role_id = r["id"]
                    break
            else:
                raise ValueError(f"Role '{role_id}' not found in guild.")
                
        await self.http.add_guild_member_role(self.guild_id, self.user.id, role_id, reason)
        
    async def remove_role(self, role_id: str, reason: str | None = None) -> None:
        if not self.guild_id or not self.user:
            raise ValueError("Member must be tied to a guild to remove roles.")
            
        if not role_id.isdigit():
            roles = await self.http.get_guild_roles(self.guild_id)
            for r in roles:
                if r.get("name", "").lower() == role_id.lower():
                    role_id = r["id"]
                    break
            else:
                raise ValueError(f"Role '{role_id}' not found in guild.")
                
        await self.http.remove_guild_member_role(self.guild_id, self.user.id, role_id, reason)
        
    async def ban(self, delete_message_seconds: int = 0, reason: str | None = None) -> None:
        if not self.guild_id or not self.user:
            raise ValueError("Member must be tied to a guild to be banned.")
        await self.http.create_guild_ban(self.guild_id, self.user.id, delete_message_seconds, reason)
        
    async def kick(self, reason: str | None = None) -> None:
        if not self.guild_id or not self.user:
            raise ValueError("Member must be tied to a guild to be kicked.")
        await self.http.remove_guild_member(self.guild_id, self.user.id, reason)

