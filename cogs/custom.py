from nextcord.ext import commands
import nextcord as discord
from nextcord import SlashOption
from data import get_commands, pick_commands
from data import add_command
from embeds import error_embed
from embeds import success_embed


class Custom(commands.Cog):
    """Create your own custom commands
    """
    def __init__(self, disclient):
        """Initialise client"""
        self.disclient = disclient

    @discord.slash_command(name='listcustom',
                           description="See a list of custom commands",
                           guild_ids=[755143761922883584])
    async def command_list(self, interaction: discord.Interaction):
        """Sends a list of all the custom commands."""
        arrr = get_commands()
        if len(arrr) == 0:
            await interaction.response.send_message(embed=error_embed('No commands added... Yet!'), ephemeral=True)
        else:
            await interaction.response.send_message(f"`{format_list(arrr.keys())}`", ephemeral=True)

    @discord.slash_command(name='custom',
                           description="customer user added commands",
                           guild_ids=[755143761922883584])
    async def custom_command(self,
                             interaction: discord.Interaction,
                             command: str = SlashOption(
                                 name="command",
                                 description="custom command to return",
                                 required=True
                             )):
        command_list = get_commands()
        if command in command_list:
            await interaction.response.send_message(command_list[command])

    @custom_command.on_autocomplete("command")
    async def _command_picker(self, interaction: discord.Interaction, command_name: str):
        if not command_name:
            await interaction.response.send_autocomplete(pick_commands())
            return
        get_near_commands = [command for command in pick_commands(near=command_name)
                             if command.lower().startswith(command_name.lower())]
        return get_near_commands

    @discord.slash_command(name='addcustom',
                           description="Get help regarding commands or command groups",
                           guild_ids=[755143761922883584])
    async def add_command(self,
                          interaction: discord.Interaction,
                          name: str = SlashOption(
                              name="name",
                              description="what the command will be called",
                              required=True
                          ),
                          gfy: str = SlashOption(
                              name="link",
                              description="the link returned from this command",
                              required=True
                          )):
        """Adds a custom command with a valid gfycat/redgif/YouTube link!
        Example: .addcommand <name> <link>
        You can now call this command with .<name>
        """
        name = name.lower()
        valid = (
            "https://gfycat.com/",
            "https://www.youtube.com/",
            "https://redgifs.com/",
            "https://www.gifdeliverynetwork.com/"
        )
        if gfy.startswith(valid):
            added = add_command(name, gfy, interaction.user.id)
            if added:
                await interaction.response.send_message(embed=success_embed(f'Added command `{name}`!'))
            else:
                await interaction.response.send_message(embed=error_embed('Something went wrong!'))
        else:
            await interaction.response.send_message(embed=error_embed('Invalid link!'))


def format_list(array):
    formatted = '`, `'.join(array)
    return formatted


def setup(disclient):
    disclient.add_cog(Custom(disclient))
