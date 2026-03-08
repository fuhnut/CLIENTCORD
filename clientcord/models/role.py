import msgspec

class Role(msgspec.Struct, kw_only=True):
    id: str
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    icon: str | None = None
    unicode_emoji: str | None = None
    tags: dict | None = None
    flags: int = 0
