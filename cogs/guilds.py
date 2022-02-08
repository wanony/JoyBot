import re

import nextcord as discord
from nextcord.ext import commands

from cogs.mods import is_mod
from data import set_guild_prefix_db, add_banned_word, remove_restricted_user, add_restricted_user, check_user_is_mod, \
    add_linked_channel_db, set_guild_max_timer_db
from embeds import error_embed, success_embed, permission_denied_embed


class Server(commands.Cog):
    """Server specific commands.
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

    @commands.command(name='set_max_timer', aliases=['maxtimer', 'setmaxtimer'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def _set_max_timer(self, ctx, timer_limit):
        """Set a timer limit for `timer` commands used in this server!
        Example:
        .set_max_timer 10"""
        guild_id = ctx.guild.id
        set_limit = set_guild_max_timer_db(timer_limit, guild_id)
        if set_limit:
            await ctx.send(embed=success_embed(f'Set the timer limit to `{timer_limit}` minute(s) in {ctx.guild.name}!'))
        else:
            await ctx.send(embed=error_embed(f'Failed to set the timer limit!'))

    @commands.command(name='restrict_user', aliases=['restrictuser'])
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def _restrict_user(self, ctx, member: discord.Member):
        """Restricts a user from using Joy's Fun category commands in this discord.
        The user can continue to use the bot in DMs, other categories, and in other discords."""
        added = add_restricted_user(ctx.guild.id, member.id)
        if added:
            await ctx.send(embed=success_embed(f'Restricted {member} in {ctx.guild.name}!'))
        else:
            await ctx.send(embed=error_embed(f'{member} is already restricted in {ctx.guild.name}!'))

    @commands.command(name='unrestrict_user', aliases=['unrestrictuser'])
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def _unrestrict_user(self, ctx, member: discord.Member):
        """Unrestricts a user from using Joy's Fun category commands in this discord."""
        removed = remove_restricted_user(ctx.guild.id, member.id)
        if removed:
            await ctx.send(embed=success_embed(f'{member} is no longer restricted in {ctx.guild.name}!'))
        else:
            await ctx.send(embed=error_embed(f'{member} is not restricted in {ctx.guild.name}!'))

    @commands.command(name='link_channel', aliases=['linkchannel', 'channellink'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @is_mod()
    async def _link_channel(self, ctx, group, idol):
        """Links channel to a member to automatically add links when posted in here"""
        group = group.lower()
        idol = idol.lower()
        added = add_linked_channel_db(ctx.channel.id, group, idol)
        if added:
            await ctx.send(embed=success_embed(f"Linked channel to automatically grab links for {group}'s {idol}!"))
        else:
            await ctx.send(embed=error_embed(f"Failed to add linked channel!"))
    #
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

    @commands.command(name='regexchannel')
    @commands.has_permissions(administrator=True)
    async def _regex_channel(self, ctx, regex=None):
        """Force a specific type of text to be sent in a channel, message that do not match will be
        automatically deleted."""
        if not regex:
            await ctx.send(embed=error_embed('No regex/text format provided!'))
            return

        if regex == 'gfy':
            pass
        elif regex == 'images':
            pass
        elif regex == 'videos':
            pass
        else:
            try:
                regex = rf'{regex}'
                reg = re.compile(regex)
            except Exception as e:
                print(e)
                await ctx.send(
                    embed=error_embed(f'Failed to compile regex!: {regex}\n'
                                      f'There is likely an error with this expression.'
                                      'Check out <https://regex101.com/> for help!'))
                return

            await ctx.send(embed=success_embed(f'Regex {regex} is now enforced in this channel!'))
            pass

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="None!"):
        """Kicks a member."""
        await member.kick(reason=reason)
        await ctx.send(
            f"{member.mention} kicked by {ctx.author} for: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="None!"):
        """Bans a member."""
        await member.ban(reason=reason)
        await ctx.send(
            f"{member.mention} banned by {ctx.author} for: {reason}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, number: int):
        """Deletes a specified number of messages in the channel
        the command is invoked in.
        """
        channel = ctx.channel
        await channel.purge(limit=number+1)
        if number == 1:
            msg = "Cleared 1 message!"
        else:
            msg = f"Cleared `{number}` messages!"
        await ctx.send(embed=success_embed(msg))


def setup(disclient):
    disclient.add_cog(Server(disclient))
