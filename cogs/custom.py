from discord.ext import commands
from data import get_commands
from data import add_command
from data import find_command
from embeds import error_embed
from embeds import success_embed


class Custom(commands.Cog):
    """This category contains commands that can be made
    by users that are for fun, such a their own memes or
    reaction gfys or youtube links.
    """
    def __init__(self, disclient):
        self.disclient = disclient

    @commands.command(aliases=['commands'])
    async def command_list(self, ctx):
        """Sends a list of all the custom commands"""
        arrr = get_commands()
        if len(arrr) == 0:
            await ctx.send(embed=error_embed('No commands added... Yet!'))
        else:
            await ctx.send(f"`{format_list(arrr.keys())}`")

    @commands.command(aliases=['ac', 'addcommand'])
    async def add_command(self, ctx, name, gfy):
        """
        Adds a custom command with a valid gfy/red/gif link!
        Example: .addcommand <name> <link>
        You can now call this command with .fun
        """
        name = name.lower()
        valid = (
            "https://gfycat.com/",
            "https://www.youtube.com/",
            "https://redgifs.com/",
            "https://www.gifdeliverynetwork.com/"
        )
        if gfy.startswith(valid):
            added = add_command(name, gfy, ctx.author.id)
            if added:
                await ctx.send(embed=success_embed(f'Added command `{name}`!'))
            else:
                await ctx.send(embed=error_embed(f'Something went wrong!'))
        else:
            await ctx.send(embed=error_embed(f'Invalid link!'))


def format_list(array):
    formatted = '`, `'.join(array)
    return formatted


def setup(disclient):
    disclient.add_cog(Custom(disclient))
