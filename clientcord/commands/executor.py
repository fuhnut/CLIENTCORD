import asyncio
from typing import Any, Callable

class ExecutionPlan:
    def __init__(self, command_name: str, instance: Any, func: Callable, injection_plan: list[Callable], middleware_chain: Any, error_handler: Callable, middleware_error_handler: Callable, option_error_handler: Callable) -> None:
        self.command_name = command_name
        self.instance = instance
        self.func = func
        self.injection_plan = injection_plan
        self.middleware_chain = middleware_chain
        self.error_handler = error_handler
        self.middleware_error_handler = middleware_error_handler
        self.option_error_handler = option_error_handler

class Executor:
    def __init__(self, injector: Any) -> None:
        self.injector = injector
        self.plans: dict[str, ExecutionPlan] = {}

    def add_plan(self, plan: ExecutionPlan) -> None:
        self.plans[plan.command_name] = plan

    async def execute(self, command_name: str, ctx: Any, payload: Any = None) -> None:
        plan = self.plans.get(command_name)
        if not plan:
            return

        if plan.middleware_chain:
            passed = await plan.middleware_chain.execute(ctx, plan.middleware_error_handler)
            if not passed:
                return

        try:
            kwargs = self.injector.execute_plan(plan.injection_plan, ctx, payload)
            if asyncio.iscoroutinefunction(plan.func):
                await plan.func(**kwargs)
            else:
                plan.func(**kwargs)
        except Exception as e:
            await plan.error_handler(ctx, str(e))
