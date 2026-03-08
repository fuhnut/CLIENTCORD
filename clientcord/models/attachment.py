import msgspec

class Attachment(msgspec.Struct, kw_only=True):
    id: str
    filename: str
    size: int
    url: str
    proxy_url: str
    description: str | None = None
    content_type: str | None = None
    height: int | None = None
    width: int | None = None
    ephemeral: bool | None = None
    duration_secs: float | None = None
    waveform: str | None = None
    flags: int | None = None
