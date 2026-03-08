import msgspec
from .user import User
from .member import Member
from .attachment import Attachment

class Message(msgspec.Struct, kw_only=True):
    id: str
    channel_id: str
    author: User
    content: str
    timestamp: str
    tts: bool
    mention_everyone: bool
    mentions: list[User]
    mention_roles: list[str]
    attachments: list[Attachment]
    embeds: list[dict]
    pinned: bool
    type: int
    edited_timestamp: str | None = None
    reactions: list[dict] = []
    nonce: str | int | None = None
    webhook_id: str | None = None
    activity: dict | None = None
    application: dict | None = None
    application_id: str | None = None
    message_reference: dict | None = None
    flags: int | None = None
    referenced_message: dict | None = None
    interaction: dict | None = None
    thread: dict | None = None
    components: list[dict] = []
    sticker_items: list[dict] = []
    stickers: list[dict] = []
    position: int | None = None
    role_subscription_data: dict | None = None
    guild_id: str | None = None
    member: Member | None = None
