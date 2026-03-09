import asyncio
from typing import Callable, Any
from ..logger import debug, error

class Dispatcher:
    __slots__ = ("handlers", "client")

    def __init__(self, client: Any = None) -> None:
        self.handlers: dict[str, list[Callable]] = {}
        self.client = client

    def add_handler(self, event: str, handler: Callable) -> None:
        event = event.upper()
        if event not in self.handlers:
            self.handlers[event] = []
        if handler not in self.handlers[event]:
            self.handlers[event].append(handler)

    def has_handler(self, event: str) -> bool:
        return event.upper() in self.handlers

    async def dispatch(self, event: str, payload: dict | Any) -> None:
        event = event.upper()
        debug(f"Dispatch {event}")
        handlers = self.handlers.get(event, [])
        for handler in handlers:
            try:
                if self.client:
                    plan = self.client.injector.build_plan(handler)
                    kwargs = self.client.injector.execute_plan(plan, None, payload)
                    if asyncio.iscoroutinefunction(handler):
                        await handler(**kwargs)
                    else:
                        handler(**kwargs)
                else:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(payload)
                    else:
                        handler(payload)
            except Exception as e:
                error(f"Event handler {event} failed: {e}")
