import asyncio
from typing import Callable, Any
from ..logger import debug, error

class Dispatcher:
    def __init__(self) -> None:
        self.handlers: dict[str, list[Callable]] = {}

    def add_handler(self, event: str, handler: Callable) -> None:
        event = event.upper()
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

    async def dispatch(self, event: str, payload: dict | Any) -> None:
        event = event.upper()
        debug(f"Dispatch {event}")
        handlers = self.handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                error(f"Event handler {event} failed: {e}")
