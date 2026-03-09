from .role import Role
from .base import ClientObject
from ..utils.permissions import Permissions
from .base import ClientObject
from .channel import ChannelType
from .auto_moderation import EventType, TriggerType, ActionType, KeywordPresetType

class Guild(ClientObject):
    id: str
    name: str | None = None
    icon: str | None = None
    icon_hash: str | None = None
    splash: str | None = None
    discovery_splash: str | None = None
    owner: bool | None = None
    owner_id: str | None = None
    permissions: str | None = None
    region: str | None = None
    afk_channel_id: str | None = None
    afk_timeout: int | None = None
    widget_enabled: bool | None = None
    widget_channel_id: str | None = None
    verification_level: int | None = None
    default_message_notifications: int | None = None
    explicit_content_filter: int | None = None
    roles: list[Role] = []
    features: list[str] = []
    mfa_level: int | None = None
    application_id: str | None = None
    system_channel_id: str | None = None
    system_channel_flags: int | None = None
    rules_channel_id: str | None = None
    max_presences: int | None = None
    max_members: int | None = None
    vanity_url_code: str | None = None
    description: str | None = None
    banner: str | None = None
    premium_tier: int | None = None
    premium_subscription_count: int | None = None
    preferred_locale: str | None = None
    public_updates_channel_id: str | None = None
    max_video_channel_users: int | None = None
    approximate_member_count: int | None = None
    approximate_presence_count: int | None = None
    welcome_screen: dict | None = None
    nsfw_level: int | None = None
    stickers: list[dict] = []
    premium_progress_bar_enabled: bool = False
    safety_alerts_channel_id: str | None = None

    async def ban(self, user_id: str, delete_message_seconds: int = 0, reason: str | None = None) -> None:
        await self.http.create_guild_ban(self.id, user_id, delete_message_seconds, reason)
        
    async def unban(self, user_id: str, reason: str | None = None) -> None:
        await self.http.remove_guild_ban(self.id, user_id, reason)
        
    async def kick(self, user_id: str, reason: str | None = None) -> None:
        await self.http.remove_guild_member(self.id, user_id, reason)

    async def fetch_audit_logs(self, user_id: str | None = None, action_type: int | None = None, before: str | None = None, after: str | None = None, limit: int = 50) -> dict:
        return await self.http.get_guild_audit_log(self.id, user_id, action_type, before, after, limit)

    async def list_auto_moderation_rules(self) -> list[dict]:
        return await self.http.list_auto_moderation_rules(self.id)

    async def get_auto_moderation_rule(self, rule_id: str) -> dict:
        return await self.http.get_auto_moderation_rule(self.id, rule_id)

    async def create_auto_moderation_rule(self, name: str, event_type: int | str, trigger_type: int | str, actions: list[dict], reason: str | None = None, **kwargs) -> dict:
        if isinstance(event_type, str):
            event_type = getattr(EventType, event_type.replace(" ", "_").lower(), 1)
        if isinstance(trigger_type, str):
            trigger_type = getattr(TriggerType, trigger_type.replace(" ", "_").lower(), 1)
            
        for action in actions:
            if isinstance(action.get("type"), str):
                action["type"] = getattr(ActionType, action["type"].replace(" ", "_").lower(), 1)
                
        if "trigger_metadata" in kwargs and "presets" in kwargs["trigger_metadata"]:
            presets = kwargs["trigger_metadata"]["presets"]
            for i, preset in enumerate(presets):
                if isinstance(preset, str):
                    presets[i] = getattr(KeywordPresetType, preset.replace(" ", "_").lower(), 1)
                    
        kwargs.update({"name": name, "event_type": event_type, "trigger_type": trigger_type, "actions": actions})
        return await self.http.create_auto_moderation_rule(self.id, kwargs, reason)

    async def modify_auto_moderation_rule(self, rule_id: str, reason: str | None = None, **kwargs) -> dict:
        return await self.http.modify_auto_moderation_rule(self.id, rule_id, kwargs, reason)

    async def delete_auto_moderation_rule(self, rule_id: str, reason: str | None = None) -> None:
        await self.http.delete_auto_moderation_rule(self.id, rule_id, reason)

    async def list_emojis(self) -> list[dict]:
        return await self.http.list_guild_emojis(self.id)

    async def get_emoji(self, emoji_id: str) -> dict:
        return await self.http.get_guild_emoji(self.id, emoji_id)

    async def create_emoji(self, name: str, image: str, reason: str | None = None, **kwargs) -> dict:
        kwargs.update({"name": name, "image": image})
        return await self.http.create_guild_emoji(self.id, kwargs, reason)

    async def modify_emoji(self, emoji_id: str, reason: str | None = None, **kwargs) -> dict:
        return await self.http.modify_guild_emoji(self.id, emoji_id, kwargs, reason)

    async def delete_emoji(self, emoji_id: str, reason: str | None = None) -> None:
        await self.http.delete_guild_emoji(self.id, emoji_id, reason)

    async def create_channel(self, name: str, type: int | str = 0, reason: str | None = None, **kwargs) -> dict:
        if isinstance(type, str):
            type_map = {
                "text": ChannelType.guild_text,
                "voice": ChannelType.guild_voice,
                "category": ChannelType.guild_category,
                "announcement": ChannelType.guild_announcement,
                "stage": ChannelType.guild_stage_voice,
                "forum": ChannelType.guild_forum,
                "media": ChannelType.guild_media
            }
            type = type_map.get(type.lower(), 0)
            
        kwargs.update({"name": name, "type": type})
        return await self.http.create_guild_channel(self.id, kwargs, reason)

    async def create_role(self, name: str, reason: str | None = None, permissions: str | int | list[str] | None = None, **kwargs) -> dict:
        kwargs.update({"name": name})
        if permissions is not None:
            kwargs["permissions"] = Permissions.resolve(permissions)
        return await self.http.create_guild_role(self.id, kwargs, reason)

    def get_member(self, member_id: str) -> Any:
        from .member import Member
        from .user import User
        import msgspec
        if not member_id: return None
        
        # Check Cache
        cached = self._client.cache.get(f"member:{self.id}:{member_id}", dict)
        if cached:
            try:
                m = msgspec.json.decode(msgspec.json.encode(cached), type=Member)
                m._client = self._client
                if m.user:
                    m.user._client = self._client
                return m
            except Exception:
                pass
        
        m = Member(guild_id=self.id)
        m.user = User(id=member_id)
        m.user._client = self._client
        m._client = self._client
        return m
