from clientcord.components import ComponentCommand, ModalCommand
from clientcord.commands.context import Context
from clientcord.declare import component, modal

@component(custom_id="demo-string-menu")
class StringMenuHandler(ComponentCommand):
    async def run(self, ctx: Context):
        selected = ctx.interaction.get("data", {}).get("values", [])
        await ctx.write(f"You selected: **{', '.join(selected)}** from the string menu!")

@component(custom_id="demo-user-menu")
class UserMenuHandler(ComponentCommand):
    async def run(self, ctx: Context):
        selected = ctx.interaction.get("data", {}).get("values", [])
        await ctx.write(f"You selected user ID: **{selected[0]}**")

@component(custom_id="demo-channel-menu")
class ChannelMenuHandler(ComponentCommand):
    async def run(self, ctx: Context):
        selected = ctx.interaction.get("data", {}).get("values", [])
        await ctx.write(f"You selected channel ID: **{selected[0]}**")

@component(custom_id="demo-role-menu")
class RoleMenuHandler(ComponentCommand):
    async def run(self, ctx: Context):
        selected = ctx.interaction.get("data", {}).get("values", [])
        await ctx.write(f"You selected role ID: **{selected[0]}**")

@component(custom_id="demo-mention-menu")
class MentionableMenuHandler(ComponentCommand):
    async def run(self, ctx: Context):
        selected = ctx.interaction.get("data", {}).get("values", [])
        await ctx.write(f"You selected mentionable ID: **{selected[0]}**")

@component(custom_id="demo-button")
class ButtonHandler(ComponentCommand):
    async def run(self, ctx: Context):
        await ctx.write("You clicked the big red button!")

@modal(custom_id="survey-modal")
class SurveyModalHandler(ModalCommand):
    async def run(self, ctx: Context):
        components = ctx.interaction.get("data", {}).get("components", [])
        name = ""
        feedback = ""
        
        for row in components:
            for comp in row.get("components", []):
                if comp.get("custom_id") == "form-name":
                    name = comp.get("value")
                elif comp.get("custom_id") == "form-feedback":
                    feedback = comp.get("value")
                    
        await ctx.write(f"Thank you for the feedback, **{name}**!\n\nYour message: {feedback}")
