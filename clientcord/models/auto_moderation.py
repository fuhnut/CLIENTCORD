import msgspec


class TriggerType:
    keyword = 1
    spam = 3
    keyword_preset = 4
    mention_spam = 5
    member_profile = 6


class EventType:
    message_send = 1
    member_update = 2


class KeywordPresetType:
    profanity = 1
    sexual_content = 2
    slurs = 3


class ActionType:
    block_message = 1
    send_alert_message = 2
    timeout = 3
    block_member_interaction = 4


class ActionMetadata(msgspec.Struct, kw_only=True):
    channel_id: str | None = None
    duration_seconds: int | None = None
    custom_message: str | None = None


class AutoModerationAction(msgspec.Struct, kw_only=True):
    type: int
    metadata: ActionMetadata | None = None


class TriggerMetadata(msgspec.Struct, kw_only=True):
    keyword_filter: list[str] = []
    regex_patterns: list[str] = []
    presets: list[int] = []
    allow_list: list[str] = []
    mention_total_limit: int | None = None
    mention_raid_protection_enabled: bool | None = None


class AutoModerationRule(msgspec.Struct, kw_only=True):
    id: str
    guild_id: str
    name: str
    creator_id: str
    event_type: int
    trigger_type: int
    trigger_metadata: TriggerMetadata
    actions: list[AutoModerationAction]
    enabled: bool
    exempt_roles: list[str] = []
    exempt_channels: list[str] = []
