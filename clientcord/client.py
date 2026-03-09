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
        self.dispatcher = Dispatcher(self)
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
                            
                            for attr_name in dir(module):
                                attr = getattr(module, attr_name)
                                if hasattr(attr, "__is_command__") or hasattr(attr, "__is_event__") or hasattr(attr, "__is_middleware__"):
                                    self.load_component(attr)
                            
                            debug(f"Auto-loaded module {file[:-3]} from {d}")

    def _register_default_services(self) -> None:
        self.container.register(Client, self)
        self.container.register(HTTPClient, self.http)
        self.container.register(LMDBCache, self.cache)

    async def execute_handler(self, handler: Any, ctx: Context, payload: dict) -> None:
        run_func = getattr(handler, "run")
        injection_plan = self.injector.build_plan(run_func)
        args, kwargs = self.injector.resolve_plan(injection_plan, {"ctx": ctx, "payload": payload})
        await run_func(*args, **kwargs)

    def load_component(self, component: Any) -> None:
        if hasattr(component, "__is_command__"):
            self.registry.add_command(component())
        elif hasattr(component, "__is_event__"):
            self.dispatcher.add_handler(component.event_name, component)
        elif hasattr(component, "__is_middleware__"):
            self.registry.add_middleware(component.middleware_name, component)
        elif hasattr(component, "__is_component_handler__"):
            self.registry.add_component_handler(component())
        elif hasattr(component, "__is_modal_handler__"):
            self.registry.add_modal_handler(component())

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
        info(f"Compiled {len(self.executor.plans)} execution plans successfully")

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
                    
                    # Handle Subcommand resolution for prefix commands
                    pos = args.get("__positional__", [])
                    if pos:
                        potential_sub = pos[0]
                        # Check all commands for matching parent and name
                        for sub_cmd in self.registry.commands.values():
                            parent = getattr(sub_cmd, "__parent__", None)
                            if parent and parent.name == cmd_name and sub_cmd.name == potential_sub:
                                cmd_name = potential_sub
                                args["__positional__"] = pos[1:]
                                break

                    cmd = self.registry.commands.get(cmd_name)
                    if cmd:
                        if getattr(cmd, "prefix", True):
                            ctx = Context(self, message=payload)
                            ctx.options = args
                            await self.executor.execute(cmd_name, ctx, payload)
                    else:
                        from .suggestions import Suggestor
                        Sug = Suggestor(list(self.registry.commands.keys()))
                        Sug.print_suggestion(cmd_name)

        async def on_interaction(payload: dict) -> None:
            t = payload.get("type")
            data = payload.get("data", {})
            
            if t == 2:
                cmd_name = data.get("name")
                if not cmd_name:
                    return

                ctx = Context(self, interaction=payload)
                options_data = data.get("options", [])
                
                # Handle Subcommands (Type 1)
                while options_data and options_data[0].get("type") == 1:
                    sub_opt = options_data[0]
                    cmd_name = sub_opt["name"]
                    options_data = sub_opt.get("options", [])
                
                for opt in options_data:
                    ctx.options[opt["name"]] = opt.get("value")
                        
                cmd = self.registry.commands.get(cmd_name)
                if cmd and getattr(cmd, "slash", True):
                    await self.executor.execute(cmd_name, ctx, payload)

            elif t == 3: # Component Interaction
                custom_id = data.get("custom_id")
                handler = self.registry.components.get(custom_id)
                if handler:
                    ctx = Context(self, interaction=payload)
                    await self.execute_handler(handler, ctx, payload)

            elif t == 5: # Modal Submit
                custom_id = data.get("custom_id")
                handler = self.registry.modals.get(custom_id)
                if handler:
                    ctx = Context(self, interaction=payload)
                    await self.execute_handler(handler, ctx, payload)

        async def on_guild_create(payload: dict) -> None:
            from .models.guild import Guild
            from .models.member import Member
            
            guild_id = payload["id"]
            self.cache.set(f"guild:{guild_id}", payload)
            
            for member_data in payload.get("members", []):
                user_id = member_data["user"]["id"]
                self.cache.set(f"member:{guild_id}:{user_id}", member_data)

        async def on_member_add(payload: dict) -> None:
            guild_id = payload["guild_id"]
            user_id = payload["user"]["id"]
            self.cache.set(f"member:{guild_id}:{user_id}", payload)

        async def on_member_update(payload: dict) -> None:
            guild_id = payload["guild_id"]
            user_id = payload["user"]["id"]
            self.cache.set(f"member:{guild_id}:{user_id}", payload)

        async def on_member_remove(payload: dict) -> None:
            guild_id = payload["guild_id"]
            user_id = payload["user"]["id"]
            self.cache.delete(f"member:{guild_id}:{user_id}")

        self.dispatcher.add_handler("MESSAGE_CREATE", on_message)
        self.dispatcher.add_handler("INTERACTION_CREATE", on_interaction)
        self.dispatcher.add_handler("GUILD_CREATE", on_guild_create)
        self.dispatcher.add_handler("GUILD_MEMBER_ADD", on_member_add)
        self.dispatcher.add_handler("GUILD_MEMBER_UPDATE", on_member_update)
        self.dispatcher.add_handler("GUILD_MEMBER_REMOVE", on_member_remove)

    async def _start(self) -> None:
        self.compile_execution_plans()
        try:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        except Exception as e:
            warn(f"Failed to fetch application info: {e}")
            
        import gc
        gc.collect()
        
        await self.gateway.connect()
        
    async def sync_commands(self, guild_id: str | None = None) -> None:
        if not self.application_id:
            try:
                app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
                self.application_id = app_data.get("id")
            except Exception as e:
                error(f"Failed to fetch application id for sync: {e}")
                return

        payload_map = {}
        for name, cmd in self.registry.commands.items():
            if not getattr(cmd, "slash", True):
                continue
            
            parent = getattr(cmd, "__parent__", None)
            if parent:
                parent_name = parent.name
                if parent_name not in payload_map:
                    payload_map[parent_name] = {
                        "name": parent_name,
                        "description": getattr(parent, "description", ""),
                        "type": getattr(parent, "type", 1),
                        "options": []
                    }
                
                sub_payload = {
                    "name": cmd.name,
                    "description": getattr(cmd, "description", ""),
                    "type": 1 # Subcommand
                }
                
                if hasattr(cmd, "__options__") and cmd.__options__:
                    ops = []
                    for k, v in cmd.__options__.items():
                        ops.append({"name": k, **v})
                    sub_payload["options"] = ops
                
                payload_map[parent_name]["options"].append(sub_payload)
            else:
                if name not in payload_map:
                    payload_map[name] = {
                        "name": cmd.name,
                        "description": getattr(cmd, "description", ""),
                        "type": getattr(cmd, "type", 1),
                        "options": []
                    }
                    
                    if hasattr(cmd, "__options__") and cmd.__options__:
                        ops = []
                        for k, v in cmd.__options__.items():
                            ops.append({"name": k, **v})
                        payload_map[name]["options"] = ops
                    
                    if getattr(cmd, "nsfw", False):
                        payload_map[name]["nsfw"] = True
        
        final_payload = list(payload_map.values())
        for p in final_payload:
            if not p["options"]:
                p.pop("options")

        if guild_id:
            await self.http.bulk_overwrite_guild_application_commands(self.application_id, guild_id, final_payload)
            info(f"Synced {len(final_payload)} commands to guild {guild_id}")
        else:
            await self.http.bulk_overwrite_global_application_commands(self.application_id, final_payload)
            info(f"Synced {len(final_payload)} commands globally")

    async def get_channel(self, channel_id: str) -> dict:
        return await self.http.get_channel(channel_id)
        
    async def list_application_emojis(self) -> dict:
        if not self.application_id:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        return await self.http.list_application_emojis(self.application_id)
        
    async def get_application_emoji(self, emoji_id: str) -> dict:
        if not self.application_id:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        return await self.http.get_application_emoji(self.application_id, emoji_id)
        
    async def get_global_commands(self) -> list[dict]:
        if not self.application_id:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        return await self.http.get_global_application_commands(self.application_id)
        
    async def create_global_command(self, **kwargs) -> dict:
        if not self.application_id:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        return await self.http.create_global_application_command(self.application_id, kwargs)
        
    async def edit_global_command(self, command_id: str, **kwargs) -> dict:
        if not self.application_id:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        return await self.http.edit_global_application_command(self.application_id, command_id, kwargs)
        
    async def delete_global_command(self, command_id: str) -> None:
        if not self.application_id:
            app_data = await self.http.request("GET", "/oauth2/applications/@me", "global")
            self.application_id = app_data.get("id")
        await self.http.delete_global_application_command(self.application_id, command_id)

    async def execute_webhook(self, webhook_id: str, webhook_token: str | None = None, content: str = "", **kwargs) -> dict | None:
        return await self.http.execute_webhook(webhook_id, webhook_token, content, **kwargs)

    async def modify_webhook(self, webhook_id: str, payload: dict, reason: str | None = None) -> dict:
        return await self.http.modify_webhook(webhook_id, payload, reason)

    async def delete_webhook(self, webhook_id: str, reason: str | None = None) -> None:
        await self.http.delete_webhook(webhook_id, reason)

    def run(self) -> None:
        try:
            asyncio.run(self._start())
        except KeyboardInterrupt:
            info("Shutting down...")
