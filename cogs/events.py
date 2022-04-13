import re

import nextcord as discord
from nextcord.ext import commands

from bot import get_prefix
from data import get_banned_words, add_guild_db
from data import get_commands
from embeds import error_embed, permission_denied_embed, banned_word_embed


class Events(commands.Cog):
    """Events that handle user errors and messages.
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient

    @commands.Cog.listener()
    @commands.has_permissions(manage_messages=True)
    async def on_message(self, message):
        if message.author == self.disclient.user:
            return

        # user = message.author
        msg = message.content.split(" ")
        # bonegrip feature
        regex_uoh = re.compile(r'\b[uU]+[oO]+[hH]+\b')
        match = re.search(regex_uoh, message.content)
        if match:
            await message.add_reaction(emoji='😭')
        try:
            if message.mentions[0] == self.disclient.user and len(message.content.split(" ")) == 1:
                msg = f'See all of my commands by typing `/`'
                embed = discord.Embed(title=f'My Prefixes',
                                      description=f'{msg}',
                                      color=discord.Color.blurple())
                await message.channel.send(embed=embed)
        except IndexError:
            pass

    @commands.Cog.listener()
    async def on_command(self, ctx):
        # will be useful for data crunching later
        pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(embed=error_embed("Command not found!"))
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed(f'Missing argument! {error}'))
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(embed=error_embed('Something went wrong!'))
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(embed=error_embed('This command does not work in DMs!'))
            return
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=permission_denied_embed())
        raise error

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        added = add_guild_db(guild.id)
        if added:
            print(f"Added guild: {guild.name}!")

    @commands.Cog.listener()
    async def on_user_join(self, ctx):
        pass


def setup(disclient):
    disclient.add_cog(Events(disclient))
