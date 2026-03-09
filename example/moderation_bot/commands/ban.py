from clientcord.declare import command, options
from clientcord.commands.options import user, string

@options(
    target=user(description="the user to ban", required=True),
    reason=string(description="the reason for the ban", required=False)
)
@command(name="ban", description="bans a user from the server", type=1, default_member_permissions=["BAN_MEMBERS"])
class BanCommand:
    async def run(self, ctx, target: str, reason: str = None):
        if not ctx.guild:
            return await ctx.write("this command can only be used in a server.")
            
        try:
            await ctx.guild.ban(user_id=target, reason=reason)
            await ctx.write(f"successfully banned <@{target}>.")
        except Exception as e:
            await ctx.write(f"failed to ban user: {e}")
