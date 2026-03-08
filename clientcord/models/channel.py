import msgspec

class Channel(msgspec.Struct, kw_only=True):
    id: str
    type: int
    guild_id: str | None = None
    position: int | None = None
    permission_overwrites: list[dict] = []
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
    thread_metadata: dict | None = None
    member: dict | None = None
    default_auto_archive_duration: int | None = None
    permissions: str | None = None
    flags: int | None = None
    total_message_sent: int | None = None
    available_tags: list[dict] = []
    applied_tags: list[str] = []
    default_reaction_emoji: dict | None = None
    default_thread_rate_limit_per_user: int | None = None
    default_sort_order: int | None = None
    default_forum_layout: int | None = None
