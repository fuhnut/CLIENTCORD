import msgspec


class Emoji(msgspec.Struct, kw_only=True):
    id: str | None = None
    name: str | None = None
    roles: list[str] = []
    user: dict | None = None
    require_colons: bool | None = None
    managed: bool | None = None
    animated: bool | None = None
    available: bool | None = None
