import msgspec
from .user import User

class Member(msgspec.Struct, kw_only=True):
    roles: list[str]
    joined_at: str
    deaf: bool
    mute: bool
    user: User | None = None
    nick: str | None = None
    avatar: str | None = None
    premium_since: str | None = None
    flags: int = 0
    pending: bool = False
    permissions: str | None = None
    communication_disabled_until: str | None = None
