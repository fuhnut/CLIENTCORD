import msgspec
from .base import ClientObject

class User(ClientObject):
    id: str
    username: str | None = None
    discriminator: str | None = None
    avatar: str | None = None
    bot: bool | None = None
    system: bool | None = None
    mfa_enabled: bool | None = None
    banner: str | None = None
    accent_color: int | None = None
    locale: str | None = None
    verified: bool | None = None
    email: str | None = None
    flags: int | None = None
    premium_type: int | None = None
    public_flags: int | None = None
    avatar_decoration_data: dict | None = None
    global_name: str | None = None
