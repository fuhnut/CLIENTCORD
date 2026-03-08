from typing import Callable, Any

class MiddlewareChain:
    def __init__(self, middlewares: list[Callable]) -> None:
        self.middlewares = middlewares

    async def execute(self, ctx: Any, stop_handler: Callable[[Any, str], Any]) -> bool:
        idx = -1
        stopped = False
        stop_reason = ""
        
        def stop(reason: str) -> None:
            nonlocal stopped, stop_reason
            stopped = True
            stop_reason = reason

        async def next_m() -> None:
            nonlocal idx
            idx += 1
            if idx < len(self.middlewares):
                await self.middlewares[idx](ctx, next_m, stop)

        await next_m()
        if stopped:
            await stop_handler(ctx, stop_reason)
            return False
        return True
