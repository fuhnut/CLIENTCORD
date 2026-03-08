import msgspec
from .role import Role

class Guild(msgspec.Struct, kw_only=True):
    id: str
    name: str
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
