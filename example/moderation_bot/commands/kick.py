from clientcord.declare import command, options
from clientcord.commands.options import user, string

@options(
    target=user(description="the user to kick", required=True),
    reason=string(description="the reason for the kick", required=False)
)
@command(name="kick", description="kicks a user from the server", type=1, default_member_permissions=["KICK_MEMBERS"])
class KickCommand:
    async def run(self, ctx, target: str, reason: str = None):
        if not ctx.guild:
            return await ctx.write("this command can only be used in a server.")
            
        try:
            await ctx.guild.kick(user_id=target, reason=reason)
            await ctx.write(f"successfully kicked <@{target}>.")
        except Exception as e:
            await ctx.write(f"failed to kick user: {e}")
