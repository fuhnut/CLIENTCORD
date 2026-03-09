import msgspec


class AuditLogEvent:
    guild_update = 1
    channel_create = 10
    channel_update = 11
    channel_delete = 12
    channel_overwrite_create = 13
    channel_overwrite_update = 14
    channel_overwrite_delete = 15
    member_kick = 20
    member_prune = 21
    member_ban_add = 22
    member_ban_remove = 23
    member_update = 24
    member_role_update = 25
    member_move = 26
    member_disconnect = 27
    bot_add = 28
    role_create = 30
    role_update = 31
    role_delete = 32
    invite_create = 40
    invite_update = 41
    invite_delete = 42
    webhook_create = 50
    webhook_update = 51
    webhook_delete = 52
    emoji_create = 60
    emoji_update = 61
    emoji_delete = 62
    message_delete = 72
    message_bulk_delete = 73
    message_pin = 74
    message_unpin = 75
    integration_create = 80
    integration_update = 81
    integration_delete = 82
    stage_instance_create = 83
    stage_instance_update = 84
    stage_instance_delete = 85
    sticker_create = 90
    sticker_update = 91
    sticker_delete = 92
    guild_scheduled_event_create = 100
    guild_scheduled_event_update = 101
    guild_scheduled_event_delete = 102
    thread_create = 110
    thread_update = 111
    thread_delete = 112
    application_command_permission_update = 121
    soundboard_sound_create = 130
    soundboard_sound_update = 131
    soundboard_sound_delete = 132
    auto_moderation_rule_create = 140
    auto_moderation_rule_update = 141
    auto_moderation_rule_delete = 142
    auto_moderation_block_message = 143
    auto_moderation_flag_to_channel = 144
    auto_moderation_user_communication_disabled = 145
    auto_moderation_quarantine_user = 146
    creator_monetization_request_created = 150
    creator_monetization_terms_accepted = 151
    onboarding_prompt_create = 163
    onboarding_prompt_update = 164
    onboarding_prompt_delete = 165
    onboarding_create = 166
    onboarding_update = 167
    home_settings_create = 190
    home_settings_update = 191


class AuditLogChange(msgspec.Struct, kw_only=True):
    key: str
    new_value: object | None = None
    old_value: object | None = None


class OptionalAuditEntryInfo(msgspec.Struct, kw_only=True):
    application_id: str | None = None
    auto_moderation_rule_name: str | None = None
    auto_moderation_rule_trigger_type: str | None = None
    channel_id: str | None = None
    count: str | None = None
    delete_member_days: str | None = None
    id: str | None = None
    members_removed: str | None = None
    message_id: str | None = None
    role_name: str | None = None
    type: str | None = None
    integration_type: str | None = None


class AuditLogEntry(msgspec.Struct, kw_only=True):
    id: str
    action_type: int
    target_id: str | None = None
    changes: list[AuditLogChange] = []
    user_id: str | None = None
    options: OptionalAuditEntryInfo | None = None
    reason: str | None = None


class AuditLog(msgspec.Struct, kw_only=True):
    audit_log_entries: list[AuditLogEntry] = []
    application_commands: list[dict] = []
    auto_moderation_rules: list[dict] = []
    guild_scheduled_events: list[dict] = []
    integrations: list[dict] = []
    threads: list[dict] = []
    users: list[dict] = []
    webhooks: list[dict] = []
