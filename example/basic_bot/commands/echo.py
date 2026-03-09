from clientcord.declare import command, options
from clientcord.commands.options import string

@options(
    text=string(description="text to echo back", required=True)
)
@command(name="echo", description="echoes text back to you", type=1)
class EchoCommand:
    async def run(self, ctx, text: str):
        await ctx.channel.send(f"you said: {text}")
        await ctx.write("i echoed your message!")
