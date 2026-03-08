from typing import Any

class Container:
    def __init__(self) -> None:
        self._services: dict[type, Any] = {}

    def register(self, typ: type, instance: Any) -> None:
        self._services[typ] = instance

    def resolve(self, typ: type) -> Any:
        return self._services.get(typ)
