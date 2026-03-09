from clientcord.components import ComponentCommand

class ClickButton(ComponentCommand):
    # This filter determines if this component handler should run
    def filter(self, ctx):
        return ctx._interaction["data"]["custom_id"] == "click_me"
        
    async def run(self, ctx):
        await ctx.write("You clicked the primary button! Awesome job.")
