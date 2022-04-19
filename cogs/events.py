import re

import nextcord as discord
from nextcord.ext import commands

from data import  add_guild_db


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
    async def on_guild_join(self, guild):
        added = add_guild_db(guild.id)
        if added:
            print(f"Added guild: {guild.name}!")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == 741066661221761135:  # This applies to Joy's server, applying default role
            joys_role_id = 741066885583470763
            role: discord.Role = member.guild.get_role(joys_role_id)
            await member.add_roles(role)


def setup(disclient):
    disclient.add_cog(Events(disclient))
