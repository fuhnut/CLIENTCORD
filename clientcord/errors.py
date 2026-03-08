class ClientcordError(Exception):
    pass

class ValidationError(ClientcordError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"Validation errors: {', '.join(errors)}")

class MiddlewareStop(ClientcordError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Middleware stopped execution: {reason}")

class CommandExecutionError(ClientcordError):
    pass

class HTTPError(ClientcordError):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")

class GatewayError(ClientcordError):
    pass
