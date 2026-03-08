from typing import Callable, Any

def command(name: str, description: str = "", default_member_permissions: list[str] | None = None, bot_permissions: list[str] | None = None, guild_ids: list[str] | None = None, aliases: list[str] | None = None, nsfw: bool = False) -> Callable:
    def decorator(cls: type) -> type:
        cls.__is_command__ = True
        cls.name = name
        cls.description = description
        cls.default_member_permissions = default_member_permissions or []
        cls.bot_permissions = bot_permissions or []
        cls.guild_ids = guild_ids or []
        cls.aliases = aliases or []
        cls.nsfw = nsfw
        return cls
    return decorator

def event(name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.__is_event__ = True
        func.event_name = name
        return func
    return decorator

def options(**kwargs: Any) -> Callable:
    def decorator(cls: type) -> type:
        cls.__options__ = kwargs
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
