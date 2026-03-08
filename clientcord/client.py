import asyncio
import inspect
import os
import importlib.util
from typing import Any, Callable

import sys
if sys.platform != "win32":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

from .config import load_config
from .logger import info, debug, warn, error
from .cache import LMDBCache
from .intents import Intents
from .container import Container
from .injector import Injector
from .http import HTTPClient
from .gateway import Gateway
from .events.dispatcher import Dispatcher
from .commands.registry import CommandRegistry
from .commands.executor import Executor, ExecutionPlan
from .commands.parser import default_prefix_parser
from .commands.context import Context
from .commands.middleware import MiddlewareChain
import msgspec
from .models.message import Message
from .models.interaction import Interaction

class Client:
    def __init__(self, token: str = None, intents: int = None, commands: dict = None) -> None:
        cfg = load_config()
        self.token = token or cfg.get("token")
        self.intents = intents or cfg.get("intents", Intents.default())
        
        default_prefix = cfg.get("prefix", "!")
        self.command_config = commands or {"prefix": lambda msg: default_prefix}
        
        self.cache = LMDBCache()
        self.container = Container()
        self.injector = Injector(self.container)
        self.http = HTTPClient(self.token)
        self.dispatcher = Dispatcher()
        self.gateway = Gateway(self.token, self.intents, self.dispatcher)
        
        self.registry = CommandRegistry()
        self.executor = Executor(self.injector)
        
        self.application_id = None
        
        self._register_default_services()
        self._setup_core_events()
        self._load_directories(cfg)

    def _load_directories(self, cfg: dict) -> None:
        dirs_to_load = []
        if "commands" in cfg: dirs_to_load.append(cfg["commands"])
        if "components" in cfg: dirs_to_load.append(cfg["components"])
        if "events" in cfg: dirs_to_load.append(cfg["events"])
        
        main_mod = sys.modules.get("__main__")
        base_dir = os.path.dirname(os.path.abspath(main_mod.__file__)) if main_mod and hasattr(main_mod, "__file__") else os.getcwd()
        
        for d in dirs_to_load:
            d = d.lstrip("/")
            target_dir = os.path.join(base_dir, d)
            if not os.path.exists(target_dir):
                warn(f"Directory {d} not found for auto-loading")
                continue
                
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        path = os.path.join(root, file)
                        spec = importlib.util.spec_from_file_location(file[:-3], path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[file[:-3]] = module
                            spec.loader.exec_module(module)
                            debug(f"Auto-loaded module {file[:-3]} from {d}")

    def _register_default_services(self) -> None:
        self.container.register(Client, self)
        self.container.register(HTTPClient, self.http)
        self.container.register(LMDBCache, self.cache)

    def load_component(self, component: Any) -> None:
        if hasattr(component, "__is_command__"):
            self.registry.add_command(component())
        elif hasattr(component, "__is_event__"):
            self.dispatcher.add_handler(component.event_name, component)
        elif hasattr(component, "__is_middleware__"):
            self.registry.add_middleware(component.middleware_name, component)

    def compile_execution_plans(self) -> None:
        for name, cmd in self.registry.commands.items():
            run_func = getattr(cmd, "run")
            injection_plan = self.injector.build_plan(run_func)
            
            mws = []
            for attr in dir(cmd):
                val = getattr(cmd, attr)
                if hasattr(val, "__is_middleware__"):
                    mws.append(val)
                    
            chain = MiddlewareChain(mws)
            
            async def default_err(ctx: Any, err: str) -> None:
                error(f"Command execution failed: {err}")
                try:
                    await ctx.write(f"Error: {err}")
                except Exception:
                    pass
                    
            async def default_mw_err(ctx: Any, reason: str) -> None:
                warn(f"Middleware stopped: {reason}")
                try:
                    await ctx.write(f"Blocked: {reason}")
                except Exception:
                    pass
                    
            async def default_opt_err(ctx: Any, errors: list[str]) -> None:
                warn(f"Option validation failed: {errors}")
                try:
                    await ctx.write(f"Invalid options: {', '.join(errors)}")
                except Exception:
                    pass
                
            err_handler = getattr(cmd, "on_error", default_err)
            mw_err_handler = getattr(cmd, "on_middleware_error", default_mw_err)
            opt_err_handler = getattr(cmd, "on_option_error", default_opt_err)
            
            plan = ExecutionPlan(
                command_name=name,
                instance=cmd,
                func=run_func,
                injection_plan=injection_plan,
                middleware_chain=chain,
                error_handler=err_handler,
                middleware_error_handler=mw_err_handler,
                option_error_handler=opt_err_handler
            )
            self.executor.add_plan(plan)
        info("Compiled execution plans successfully")

    def _setup_core_events(self) -> None:
        async def on_message(payload: dict) -> None:
            content = payload.get("content", "")
            prefix_resolver = self.command_config.get("prefix")
            if prefix_resolver:
                prefixes = prefix_resolver(payload)
                if isinstance(prefixes, str):
                    prefixes = [prefixes]
                
                parser = self.command_config.get("parser", default_prefix_parser)
                parsed = parser(content, prefixes)
                
                if parsed:
                    cmd_name, args = parsed
                    ctx = Context(self, message=payload)
                    ctx.options = args
                    await self.executor.execute(cmd_name, ctx, payload)

        async def on_interaction(payload: dict) -> None:
            t = payload.get("type")
            if t == 2:
                cmd_name = payload["data"].get("name")
                if not cmd_name:
                    return
                ctx = Context(self, interaction=payload)
                
                options_data = payload["data"].get("options", [])
                for opt in options_data:
                    ctx.options[opt["name"]] = opt.get("value")
                    
                await self.executor.execute(cmd_name, ctx, payload)

        self.dispatcher.add_handler("MESSAGE_CREATE", on_message)
        self.dispatcher.add_handler("INTERACTION_CREATE", on_interaction)

    async def _start(self) -> None:
        self.compile_execution_plans()
        try:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        except Exception as e:
            warn(f"Failed to fetch application info: {e}")
            
        await self.gateway.connect()
        
    def run(self) -> None:
        try:
            asyncio.run(self._start())
        except KeyboardInterrupt:
            info("Shutting down...")
