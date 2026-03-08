import inspect
from typing import Callable, Any
from .container import Container

class Injector:
    def __init__(self, container: Container) -> None:
        self.container = container

    def build_plan(self, func: Callable) -> list[Callable[[Any, Any], dict[str, Any]]]:
        sig = inspect.signature(func)
        plan = []
        
        for name, param in sig.parameters.items():
            if name == "self":
                continue
                
            if name == "ctx":
                plan.append(lambda ctx, _, n=name: {n: ctx})
                continue
                
            typ = param.annotation
            if typ is inspect.Parameter.empty:
                plan.append(lambda ctx, _, n=name: {})
                continue

            service = self.container.resolve(typ)
            if service is not None:
                plan.append(lambda ctx, _, s=service, n=name: {n: s})
                continue
                
            plan.append(lambda ctx, payload, t=typ, n=name: {n: ctx.resolve(t, payload)})
            
        return plan

    def execute_plan(self, plan: list[Callable], ctx: Any, payload: Any) -> dict[str, Any]:
        kwargs = {}
        for step in plan:
            kwargs.update(step(ctx, payload))
        return kwargs
