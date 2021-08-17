import discord
from discord.ext import commands

from bot import get_prefix
from data import get_banned_words, add_guild_db, apis_dict
from data import get_commands
import re
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
        # regexuoh = re.compile("^u|U+o|O+h|H+$")
        # match = re.search(regexuoh, message.content)
        # if match:
        #     await message.add_reaction(emoji='😭')
        if message.guild:
            guild = message.guild.id
            banned_words = get_banned_words(guild)
            if banned_words:
                w = any(x in banned_words for x in msg)
                if w:
                    await message.delete()
                    await message.author.send(banned_word_embed(message.guild, w))
        try:
            if msg[0].startswith(get_prefix(self.disclient, message)):
                command = msg[0][1:]
                command_list = get_commands()
                if command in command_list:
                    await message.channel.send(command_list[command])
        except TypeError:
            pass
        try:
            if message.mentions[0] == self.disclient.user and len(message.content.split(" ")) == 1:
                if message.guild:
                    msg = f'My prefix in this server is `{get_prefix(self.disclient, message)[-1]}`!'
                else:
                    msg = f'My prefix is `{get_prefix(self.disclient, message)[-1]}`!'
                mention = f'\nYou can always mention me to use the commands, try @{self.disclient.user.name} help'
                embed = discord.Embed(title=f'My Prefixes',
                                      description=msg + mention,
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
            async for message in ctx.history(limit=1):
                if message.author == self.disclient.user:
                    print("sent out a custom command")
                else:
                    prefix = get_prefix(self.disclient, ctx.message)[0]
                    # once guild prefix is enabled need to change regex
                    regexstr = r'(\..*){}|\{}\{}.*$'.format('{2,}', prefix, prefix)
                    print(regexstr)
                    regex2 = re.compile(regexstr)
                    # regex1 = re.compile(r'(\..*){2,}')
                    match = re.search(regex2, message.content)
                    if match:
                        print('user wrote some ...')
                    else:
                        await ctx.send(embed=error_embed("Command not found!"))
                        # raise error
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed(f'Missing argument! {error}'))
        # always raise errors
        if isinstance(error, commands.CommandInvokeError):
            if ctx.command.name == 'timer':
                return
            else:
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
