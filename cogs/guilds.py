from discord.ext import commands

from data import set_guild_prefix_db, add_banned_word
from embeds import error_embed, success_embed


class Server(commands.Cog):
    """
    Server specific commands.
    """
    def __init__(self, disclient):
        self.disclient = disclient

    @commands.command(name='set_prefix', aliases=['setprefix', 'prefix'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set_command_prefix(self, ctx, prefix):
        prefix = prefix.strip()
        if len(prefix) > 3:
            await ctx.send(embed=error_embed(f'Invalid prefix: `{prefix}. Please use 3 characters maximum'))
            return
        set_prefix = set_guild_prefix_db(ctx.guild.id, prefix)
        if set_prefix:
            await ctx.send(embed=success_embed(f'Changed this servers prefix to `{prefix}`!'))
        else:
            await ctx.send(embed=error_embed('Failed to change the prefix in this server.'))

    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # @commands.guild_only()
    # async def ban_word(self, ctx, word):
    #     """Add a word to a ban-list, if said the message will be automatically deleted."""
    #     guild_id = ctx.guild.id
    #     author_id = ctx.author.id
    #     word = word.lower()
    #     add_word = add_banned_word(guild_id, word, author_id)
    #     if add_word:
    #         await ctx.send(success_embed(f"Added ||{word}|| to banned words!"))
    #     else:
    #         await ctx.send(error_embed(f"Failed to add ||{word}|| to banned words!"))
    #
    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # @commands.guild_only()
    # async def unban_word(self, ctx, word):
    #     """Removes a word from the ban-list of this server."""
    #     guild_id = ctx.guild.id
    #     word = word.lower()
    #     add_word = add_banned_word(guild_id, word)
    #     if add_word:
    #         await ctx.send(success_embed(f"Added ||{word}|| to banned words!"))
    #     else:
    #         await ctx.send(error_embed(f"Failed to add ||{word}|| to banned words!"))


def setup(disclient):
    disclient.add_cog(Server(disclient))
