import msgspec
from .base import ClientObject

class ApplicationCommandType:
    chat_input = 1
    user = 2
    message = 3

class ApplicationCommandOptionType:
    sub_command = 1
    sub_command_group = 2
    string = 3
    integer = 4
    boolean = 5
    user = 6
    channel = 7
    role = 8
    mentionable = 9
    number = 10
    attachment = 11

class ApplicationCommandOptionChoice(msgspec.Struct, kw_only=True):
    name: str
    value: str | int | float
    name_localizations: dict | None = None

class ApplicationCommandOption(msgspec.Struct, kw_only=True):
    type: int
    name: str
    description: str
    name_localizations: dict | None = None
    description_localizations: dict | None = None
    required: bool | None = None
    choices: list[ApplicationCommandOptionChoice] | None = None
    options: list['ApplicationCommandOption'] | None = None
    channel_types: list[int] | None = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    autocomplete: bool | None = None

class ApplicationCommand(ClientObject):
    id: str | None = None
    type: int | None = None
    application_id: str | None = None
    guild_id: str | None = None
    name: str | None = None
    name_localizations: dict | None = None
    description: str | None = None
    description_localizations: dict | None = None
    options: list[ApplicationCommandOption] | None = None
    default_member_permissions: str | None = None
    dm_permission: bool | None = None
    nsfw: bool | None = None
    version: str | None = None
