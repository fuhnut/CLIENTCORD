from clientcord.declare import command
from clientcord.components import ActionRow, Button
from clientcord.components.types import ButtonStyle

@command(name="menu", description="opens a menu of component options", type=1)
class MenuCommand:
    async def run(self, ctx):
        row = ActionRow().add_components(
            Button()
            .set_custom_id("click_me")
            .set_label("click me!")
            .set_style(ButtonStyle.primary),
            
            Button()
            .set_url("https://github.com/fuhnut/CLIENTCORD")
            .set_label("view source")
            .set_style(ButtonStyle.link)
        )
        await ctx.write("here is a menu with buttons:", components=[row])
