from clientcord.declare import command, options
from clientcord.commands.context import Context

def parse_id(val: str | None) -> str | None:
    if not val: return None
    return val.replace("<@", "").replace(">", "").replace("!", "").replace("&", "")

@command(
    name="admin",
    description="Showcasing guild moderation features.",
    default_member_permissions=["administrator"]
)
class AdminCommand:
    async def run(self, ctx: Context):
        await ctx.write("Select a sub-command to execute.")

@options(
    target={"description": "The user to kick (mention or ID)", "type": "text", "required": True}
)
@command(name="kick", description="Kick a member from the guild.")
class KickCommand:
    __parent__ = AdminCommand

    async def run(self, ctx: Context):
        # Resolve from slash options or first positional arg for prefix
        raw_target = ctx.options.get("target") or (ctx.options.get("__positional__")[0] if ctx.options.get("__positional__") else None)
        target_id = parse_id(raw_target)

        if not target_id:
            return await ctx.write("Missing target user ID option! E.g. `!admin kick 12345` or `@user`")
            
        target = ctx.guild.get_member(target_id)
        if not target:
            return await ctx.write("Member not found in guild cache.")

        try:
            await target.kick(reason="Requested by Admin Showcase")
            await ctx.write(f"Kicked member {target.user.username} successfully.")
        except Exception as e:
            await ctx.write(f"Failed to kick member: {str(e)}")

@options(
    target={"description": "The user to ban (mention or ID)", "type": "text", "required": True}
)
@command(name="ban", description="Ban a member from the guild.")
class BanCommand:
    __parent__ = AdminCommand

    async def run(self, ctx: Context):
        raw_target = ctx.options.get("target") or (ctx.options.get("__positional__")[0] if ctx.options.get("__positional__") else None)
        target_id = parse_id(raw_target)

        if not target_id:
            return await ctx.write("Missing target user ID option! E.g. `!admin ban 12345` or `@user`")
            
        target = ctx.guild.get_member(target_id)
        if not target:
            return await ctx.write("Member not found in guild cache.")

        try:
            await target.ban(reason="Requested by Admin Showcase")
            await ctx.write(f"Banned member {target.user.username} successfully.")
        except Exception as e:
            await ctx.write(f"Failed to ban member: {str(e)}")

@options(
    target={"description": "The user to promote (mention or ID)", "type": "text", "required": True},
    role={"description": "The role name to grant", "type": "text", "required": False}
)
@command(name="promote", description="Dynamically grant a role by name.")
class PromoteCommand:
    __parent__ = AdminCommand

    async def run(self, ctx: Context):
        pos = ctx.options.get("__positional__", [])
        raw_target = ctx.options.get("target") or (pos[0] if pos else None)
        target_id = parse_id(raw_target)
        role_name = ctx.options.get("role") or (pos[1] if len(pos) > 1 else "Moderator")

        if not target_id:
            return await ctx.write(f"Missing target user ID option! E.g. `!admin promote 12345 {role_name}` or `@user`")
            
        target = ctx.guild.get_member(target_id)
        if not target:
            return await ctx.write("Member not found in guild cache.")

        try:
            # Clientcord dynamically resolves the string 'role_name' to a role ID
            await target.add_role(role_name, reason="Requested by Admin Showcase")
            await ctx.write(f"Promoted {target.user.username} to {role_name} successfully.")
        except Exception as e:
            await ctx.write(f"Failed to promote member: {str(e)}")

@command(name="automod", description="Create an auto-moderation rule protecting against slurs.")
class AutoModCommand:
    __parent__ = AdminCommand

    async def run(self, ctx: Context):
        try:
            await ctx.guild.create_auto_moderation_rule(
                name="Profanity Filter Showcase",
                event_type="message_send",
                trigger_type="keyword",
                trigger_metadata={"presets": ["profanity", "slurs", "sexual_content"]},
                actions=[
                    {"type": "block_message", "metadata": {"custom_message": "Please keep the chat clean!"}}
                ]
            )
            await ctx.write("Successfully generated a profanity auto-moderation rule for the guild!")
        except Exception as e:
            await ctx.write(f"Failed to create auto-moderation rule: {str(e)}")
