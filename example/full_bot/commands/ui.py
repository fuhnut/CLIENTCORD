from clientcord.declare import command
from clientcord.commands.context import Context
from clientcord.components import (
    ActionRow,
    Button,
    ButtonStyle,
    StringSelectMenu,
    UserSelectMenu,
    ChannelSelectMenu,
    RoleSelectMenu,
    MentionableSelectMenu,
    Modal,
    TextInput,
    TextInputStyle
)

@command(name="menus", description="Creates an interactive message featuring every select menu type.")
class InteractiveMenusCommand:
    async def run(self, ctx: Context):
        string_menu = (
             StringSelectMenu()
             .set_custom_id("demo-string-menu")
             .set_placeholder("Pick an option...")
             .set_options([
                 {"label": "Option A", "value": "a", "description": "Select me!"},
                 {"label": "Option B", "value": "b"}
             ])
        )

        user_menu = UserSelectMenu().set_custom_id("demo-user-menu").set_placeholder("Select a user...")
        channel_menu = ChannelSelectMenu().set_custom_id("demo-channel-menu").set_placeholder("Select a channel...")
        role_menu = RoleSelectMenu().set_custom_id("demo-role-menu").set_placeholder("Select a role...")
        mention_menu = MentionableSelectMenu().set_custom_id("demo-mention-menu").set_placeholder("Select anything mentionable...")

        r1 = ActionRow().add_components(string_menu)
        r2 = ActionRow().add_components(user_menu)
        r3 = ActionRow().add_components(channel_menu)
        r4 = ActionRow().add_components(role_menu)
        r5 = ActionRow().add_components(mention_menu)

        await ctx.write(
            "Here is every single type of Select Menu dynamically generated via the Builder pattern:",
            components=[r1, r2, r3, r4, r5]
        )

@command(name="form", description="Prompts the user with a Modal input popup overlay.")
class PopFormCommand:
    async def run(self, ctx: Context):
        name_input = (
             TextInput()
             .set_custom_id("form-name")
             .set_label("What is your name?")
             .set_style(TextInputStyle.short)
             .set_required(True)
        )

        feedback_input = (
             TextInput()
             .set_custom_id("form-feedback")
             .set_label("Any feedback about Clientcord?")
             .set_style(TextInputStyle.paragraph)
             .set_required(False)
        )

        modal = (
             Modal()
             .set_title("Customer Feedback Survey")
             .set_custom_id("survey-modal")
             .set_components([
                 ActionRow().add_components(name_input),
                 ActionRow().add_components(feedback_input)
             ])
        )

        await ctx.show_modal(modal)

@command(name="button", description="Sends an interactive button component.")
class InteractiveButtonCommand:
    async def run(self, ctx: Context):
        btn = (
             Button()
             .set_custom_id("demo-button")
             .set_label("Click Me!")
             .set_style(ButtonStyle.danger)
        )
        
        row = ActionRow().add_components(btn)
        await ctx.write("Here is a dangerously red button component:", components=[row])
