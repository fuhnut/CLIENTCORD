import msgspec

class User(msgspec.Struct, kw_only=True):
    id: str
    username: str
    discriminator: str
    avatar: str | None = None
    bot: bool = False
    system: bool = False
    mfa_enabled: bool = False
    banner: str | None = None
    accent_color: int | None = None
    locale: str | None = None
    verified: bool = False
    email: str | None = None
    flags: int = 0
    premium_type: int = 0
    public_flags: int = 0
    avatar_decoration_data: dict | None = None
    global_name: str | None = None
