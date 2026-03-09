import msgspec
from .base import ClientObject



class ChannelType:
    guild_text = 0
    dm = 1
    guild_voice = 2
    group_dm = 3
    guild_category = 4
    guild_announcement = 5
    announcement_thread = 10
    public_thread = 11
    private_thread = 12
    guild_stage_voice = 13
    guild_directory = 14
    guild_forum = 15
    guild_media = 16


class VideoQualityMode:
    auto = 1
    full = 2


class SortOrderType:
    latest_activity = 0
    creation_date = 1


class ForumLayoutType:
    not_set = 0
    list_view = 1
    gallery_view = 2


class Overwrite(msgspec.Struct, kw_only=True):
    id: str
    type: int
    allow: str
    deny: str


class ThreadMetadata(msgspec.Struct, kw_only=True):
    archived: bool
    auto_archive_duration: int
    archive_timestamp: str
    locked: bool
    invitable: bool | None = None
    create_timestamp: str | None = None


class ThreadMember(msgspec.Struct, kw_only=True):
    join_timestamp: str
    flags: int
    id: str | None = None
    user_id: str | None = None
    member: dict | None = None


class DefaultReaction(msgspec.Struct, kw_only=True):
    emoji_id: str | None = None
    emoji_name: str | None = None


class ForumTag(msgspec.Struct, kw_only=True):
    id: str
    name: str
    moderated: bool
    emoji_id: str | None = None
    emoji_name: str | None = None


class FollowedChannel(msgspec.Struct, kw_only=True):
    channel_id: str
    webhook_id: str


class Channel(ClientObject):
    id: str
    type: int | None = None
    guild_id: str | None = None
    position: int | None = None
    permission_overwrites: list[Overwrite] = []
    name: str | None = None
    topic: str | None = None
    nsfw: bool | None = None
    last_message_id: str | None = None
    bitrate: int | None = None
    user_limit: int | None = None
    rate_limit_per_user: int | None = None
    recipients: list[dict] = []
    icon: str | None = None
    owner_id: str | None = None
    application_id: str | None = None
    managed: bool | None = None
    parent_id: str | None = None
    last_pin_timestamp: str | None = None
    rtc_region: str | None = None
    video_quality_mode: int | None = None
    message_count: int | None = None
    member_count: int | None = None
    thread_metadata: ThreadMetadata | None = None
    member: ThreadMember | None = None
    default_auto_archive_duration: int | None = None
    permissions: str | None = None
    flags: int | None = None
    total_message_sent: int | None = None
    available_tags: list[ForumTag] = []
    applied_tags: list[str] = []
    default_reaction_emoji: DefaultReaction | None = None
    default_thread_rate_limit_per_user: int | None = None
    default_sort_order: int | None = None
    default_forum_layout: int | None = None

    async def send(self, content: str = "", **kwargs) -> dict:
        if "components" in kwargs and isinstance(kwargs["components"], list):
            kwargs["components"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in kwargs["components"]]
        return await self.http.send_message(self.id, content, **kwargs)
        
    async def edit(self, reason: str | None = None, **kwargs) -> dict:
        return await self.http.modify_channel(self.id, kwargs, reason)
        
    async def delete(self, reason: str | None = None) -> dict:
        return await self.http.delete_channel(self.id, reason)

    async def edit_permissions(self, overwrite_id: str, reason: str | None = None, **kwargs) -> None:
        await self.http.edit_channel_permissions(self.id, overwrite_id, kwargs, reason)

    async def delete_permission(self, overwrite_id: str, reason: str | None = None) -> None:
        await self.http.delete_channel_permission(self.id, overwrite_id, reason)

    async def get_invites(self) -> list[dict]:
        return await self.http.get_channel_invites(self.id)

    async def create_invite(self, reason: str | None = None, **kwargs) -> dict:
        return await self.http.create_channel_invite(self.id, kwargs, reason)

    async def follow(self, webhook_channel_id: str, reason: str | None = None) -> dict:
        return await self.http.follow_announcement_channel(self.id, webhook_channel_id, reason)

    async def trigger_typing(self) -> None:
        await self.http.trigger_typing(self.id)

    async def start_thread_from_message(self, message_id: str, reason: str | None = None, **kwargs) -> dict:
        return await self.http.start_thread_from_message(self.id, message_id, kwargs, reason)

    async def start_thread(self, name: str, reason: str | None = None, **kwargs) -> dict:
        kwargs.update({"name": name})
        return await self.http.start_thread(self.id, kwargs, reason)

    async def join_thread(self) -> None:
        await self.http.join_thread(self.id)

    async def leave_thread(self) -> None:
        await self.http.leave_thread(self.id)

    async def add_thread_member(self, user_id: str) -> None:
        await self.http.add_thread_member(self.id, user_id)

    async def remove_thread_member(self, user_id: str) -> None:
        await self.http.remove_thread_member(self.id, user_id)

    async def list_thread_members(self, with_member: bool = False, after: str | None = None, limit: int = 100) -> list[dict]:
        return await self.http.list_thread_members(self.id, with_member, after, limit)

    async def list_public_archived_threads(self, before: str | None = None, limit: int | None = None) -> dict:
        return await self.http.list_public_archived_threads(self.id, before, limit)

    async def list_private_archived_threads(self, before: str | None = None, limit: int | None = None) -> dict:
        return await self.http.list_private_archived_threads(self.id, before, limit)

    async def list_joined_private_archived_threads(self, before: str | None = None, limit: int | None = None) -> dict:
        return await self.http.list_joined_private_archived_threads(self.id, before, limit)
