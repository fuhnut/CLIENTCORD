import msgspec
from .base import ClientObject

class Role(ClientObject):
    id: str
    name: str | None = None
    color: int | None = None
    hoist: bool | None = None
    position: int | None = None
    permissions: str | None = None
    managed: bool | None = None
    mentionable: bool | None = None
    icon: str | None = None
    unicode_emoji: str | None = None
    tags: dict | None = None
    flags: int = 0
