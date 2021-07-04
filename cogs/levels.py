import discord
from discord.ext import commands
from data import find_user, add_user, add_user_xp
from data import get_leaderboard


class Levels(commands.Cog):
    """Levels, XP, and contribution handling commands found here
    will let users get information about levels and leaderboards
    of the top contributors!
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.disclient.user:
            return
        if message.author.bot:
            return
        author = str(message.author.id)
        found = find_user(author)
        if not found:
            add_user(author)
        add_user_xp(author)
        # add better leveling system in the future

    @commands.command(aliases=['xp'])
    async def level(self, ctx, member: discord.Member = None):
        """Returns information of the users level"""
        if member:
            member = member
        else:
            member = ctx.author
        user = find_user(member.id)
        if user:
            xp = user[1]
            cont = user[2]
            embed = discord.Embed(colour=member.colour, title="Level & XP")
            embed.set_author(name=member)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}",
                             icon_url=ctx.author.avatar_url)
            # need to update level later
            embed.add_field(name="Level:", value=xp // 100)
            embed.add_field(name="XP:", value=xp)
            embed.add_field(name="Contribution:", value=cont)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Member has no XP!")

    @commands.command()
    async def leaderboard(self, ctx, number_of_users=10):
        """Returns a leaderboard of the top 10 contributers!
        This leaderboard is made from all contributers across
        every server the bot is connected to.
        """
        async with ctx.channel.typing():
            lb = get_leaderboard(number_of_users)
            one_str = ""
            suffix = 'st.'
            for i, pair in enumerate(lb, start=1):
                if i == 2:
                    suffix = 'nd.'
                elif i == 3:
                    suffix = 'rd.'
                elif i > 3:
                    suffix = 'th.'
                user = await self.disclient.fetch_user(pair[0])
                name = user.name + '#' + user.discriminator
                spacing = 40 - len(str(i) + suffix + name)
                elem = f"`{i}{suffix} {name}{' ' * spacing}{pair[1]}`\n"
                one_str = one_str + elem
                # possibly make this string all in one field?
                # embed.add_field(name="-", value=elem, inline=False)
            embed = discord.Embed(title="Contribution Leaderboard",
                                  description=one_str,
                                  color=discord.Color.blurple())
            await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Levels(disclient))
