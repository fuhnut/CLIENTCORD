from typing import Callable, Any
from .utils.permissions import Permissions

def command(name: str, description: str = "", type: int = 1, contexts: list[int] | None = None, integration_types: list[int] | None = None, default_member_permissions: list[str] | int | str | None = None, bot_permissions: list[str] | int | str | None = None, guild_ids: list[str] | None = None, aliases: list[str] | None = None, nsfw: bool = False, slash: bool = False, prefix: bool = False, hybrid: bool = False) -> Callable:
    def decorator(cls: type) -> type:
        cls.__is_command__ = True
        cls.name = name
        cls.description = description
        cls.type = type
        cls.contexts = contexts or []
        cls.integration_types = integration_types or []
        cls.default_member_permissions = Permissions.resolve(default_member_permissions)
        cls.bot_permissions = Permissions.resolve(bot_permissions)
        cls.guild_ids = guild_ids or []
        cls.aliases = aliases or []
        cls.nsfw = nsfw

        is_hybrid = hybrid if hybrid else (not slash and not prefix)
        cls.slash = slash or is_hybrid
        cls.prefix = prefix or is_hybrid
        cls.hybrid = is_hybrid
        
        return cls
    return decorator

def event(name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.__is_event__ = True
        func.event_name = name
        return func
    return decorator

def get_option_type(typ: str | int) -> int:
    if isinstance(typ, int):
        return typ
    
    mapping = {
        "text": 3,
        "string": 3,
        "integer": 4,
        "number": 4,
        "bool": 5,
        "boolean": 5,
        "user": 6,
        "channel": 7,
        "role": 8,
        "mention": 9,
        "mentionable": 9,
        "number": 10,
        "float": 10,
        "attachment": 11,
        "subcommand": 1,
        "sub_command": 1
    }
    return mapping.get(typ.lower(), 3)

def options(**kwargs: Any) -> Callable:
    def decorator(cls: type) -> type:
        resolved_options = {}
        for name, data in kwargs.items():
            if isinstance(data, dict):
                opt = data.copy()
                opt["type"] = get_option_type(opt.get("type", "text"))
                resolved_options[name] = opt
            else:
                resolved_options[name] = {"type": get_option_type(data), "description": f"The {name} option"}
                
        cls.__options__ = resolved_options
        return cls
    return decorator

def middleware(name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.__is_middleware__ = True
        func.middleware_name = name
        return func
    return decorator

def task(interval: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.__is_task__ = True
        func.task_interval = interval
        return func
    return decorator

def component(custom_id: str) -> Callable:
    def decorator(cls: type) -> type:
        cls.__is_component_handler__ = True
        cls.custom_id = custom_id
        return cls
    return decorator

def modal(custom_id: str) -> Callable:
    def decorator(cls: type) -> type:
        cls.__is_modal_handler__ = True
        cls.custom_id = custom_id
        return cls
    return decorator
