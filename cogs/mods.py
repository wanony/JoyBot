import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """Commands for server moderation.
    """
    def __init__(self, disclient):
        self.disclient = disclient

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="None!"):
        """Kicks a member"""
        await member.kick(reason=reason)
        await ctx.send(
                    f"{member.mention} kicked by {ctx.author} for: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="None!"):
        """Bans a member"""
        await member.ban(reason=reason)
        await ctx.send(
                    f"{member.mention} banned by {ctx.author} for: {reason}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, number: int):
        """
        Deletes a specified number of messages in the channel
        the command is invoked in
        """
        channel = ctx.channel
        await channel.purge(limit=number+1)
        if number == 1:
            msg = "Cleared 1 message!"
        else:
            msg = f"Cleared `{number}` messages!"
        embed = discord.Embed(title="Success!",
                              description=msg,
                              color=discord.Color.green())
        await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Moderation(disclient))
