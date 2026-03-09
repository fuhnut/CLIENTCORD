from clientcord.declare import command
from clientcord.commands.context import Context

@command(name="utilities", description="Exposes various generic commands for auditing, emojis and channels.")
class UtilitiesCommand:
    async def run(self, ctx: Context):
        await ctx.write("Select a sub-command to execute.")

@command(name="audit", description="Fetch the last 5 audit logs from the guild.")
class AuditLogsCommand:
    __parent__ = UtilitiesCommand

    async def run(self, ctx: Context):
        logs = await ctx.guild.fetch_audit_logs(limit=5)
        entries = logs.get("audit_log_entries", [])
        
        if not entries:
            return await ctx.write("No audit logs found recently.")
            
        formatted = "\n".join([f"- Action {e.get('action_type')} by <@{e.get('user_id')}> against {e.get('target_id')}" for e in entries])
        await ctx.write(f"**Latest Audit Logs:**\n{formatted}")

@command(name="createchannel", description="Creates a new voice channel using string routing mapping.")
class VoiceChannelCommand:
    __parent__ = UtilitiesCommand

    async def run(self, ctx: Context):
        name = ctx.options.get("name", "Test Voice Channel")
        try:
            # Clientcord converts string "voice" to Guild Voice channel integer 2 automatically
            await ctx.guild.create_channel(name=name, type="voice", reason="Created by Clientcord utilities")
            await ctx.write(f"Voice Channel '{name}' created successfully!")
        except Exception as e:
            await ctx.write(f"Failed to create channel: {e}")

@command(name="emoji", description="Fetches and lists all application emojis.")
class EmojiListCommand:
    __parent__ = UtilitiesCommand

    async def run(self, ctx: Context):
        emojis = await ctx.client.list_application_emojis()
        items = emojis.get("items", [])
        
        if not items:
            return await ctx.write("This application has no uploaded global App Emojis.")
            
        emoji_list = ", ".join([e.get('name') for e in items])
        await ctx.write(f"**App Emojis:** {emoji_list}")
