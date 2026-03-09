from clientcord.declare import command
from clientcord.commands.context import Context

@command(name="slashonly", description="This command only works as a Slash Command.", slash=True)
class SlashOnlyCommand:
    async def run(self, ctx: Context):
        await ctx.write("Success! I was triggered exclusively through the Discord Slash Command UI.")

@command(name="prefixonly", description="This command only works via Prefix triggers.", prefix=True)
class PrefixOnlyCommand:
    async def run(self, ctx: Context):
        await ctx.write("Success! I was triggered explicitly through a plaintext message prefix. (Slash triggers will ignore me).")

@command(name="hybrid", description="This command works through both Slash and Prefix triggers.", hybrid=True)
class HybridCommand:
    async def run(self, ctx: Context):
        await ctx.write("Success! I am a full hybrid command and can be triggered seamlessly via whatever method you prefer.")
