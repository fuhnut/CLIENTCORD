import msgspec
from .user import User
from .member import Member
from .message import Message

class Interaction(msgspec.Struct, kw_only=True):
    id: str
    application_id: str
    type: int
    token: str
    version: int
    data: dict | None = None
    guild_id: str | None = None
    channel: dict | None = None
    channel_id: str | None = None
    member: Member | None = None
    user: User | None = None
    message: Message | None = None
    app_permissions: str | None = None
    locale: str | None = None
    guild_locale: str | None = None
    entitlements: list[dict] = []
