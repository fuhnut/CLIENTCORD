from typing import Any

class CommandRegistry:
    def __init__(self) -> None:
        self.commands: dict[str, Any] = {}
        self.middlewares: dict[str, Any] = {}
        self.components: dict[str, Any] = {}
        self.modals: dict[str, Any] = {}
        
    def add_command(self, cmd: Any) -> None:
        self.commands[cmd.name] = cmd

    def add_component_handler(self, handler: Any) -> None:
        self.components[handler.custom_id] = handler

    def add_modal_handler(self, handler: Any) -> None:
        self.modals[handler.custom_id] = handler
        
    def add_middleware(self, name: str, func: Any) -> None:
        self.middlewares[name] = func
