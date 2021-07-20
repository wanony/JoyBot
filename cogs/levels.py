import discord
from discord.ext import commands
from data import find_user, add_user, add_user_xp, get_idol_leaderboard, get_group_leaderboard
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
        if number_of_users > 20:
            number_of_users = 20
        async with ctx.channel.typing():
            lb = get_leaderboard(number_of_users)
            one_str = ""
            for i, pair in enumerate(lb, start=1):
                if str(i).endswith('1') and i != 11:
                    suffix = 'st.'
                elif str(i).endswith('2') and i != 12:
                    suffix = 'nd.'
                elif str(i).endswith('3') and i != 13:
                    suffix = 'rd.'
                else:
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

    @commands.command()
    async def idol_leaderboard(self, ctx, number_of_entries=10):
        """Returns a leaderboard of the idols with the most links added to them!"""
        if number_of_entries > 50:
            number_of_entries = 50
        async with ctx.channel.typing():
            lb = get_idol_leaderboard(number_of_entries)
            one_str = ""
            for i, triple in enumerate(lb, start=1):
                if str(i).endswith('1') and i != 11:
                    suffix = 'st.'
                elif str(i).endswith('2') and i != 12:
                    suffix = 'nd.'
                elif str(i).endswith('3') and i != 13:
                    suffix = 'rd.'
                else:
                    suffix = 'th.'
                name = triple[0].title()
                group = triple[1]
                link_count = triple[-1]
                spacing = 40 - len(str(i) + str(suffix) + str(name) + str(group)) - 3
                elem = f"`{i}{suffix} {name} ({group}) {' ' * spacing}{link_count}`\n"
                one_str = one_str + elem
            embed = discord.Embed(title="Idol Leaderboard",
                                  description=one_str,
                                  color=discord.Color.blurple())
            await ctx.send(embed=embed)

    @commands.command()
    async def group_leaderboard(self, ctx, number_of_entries=10):
        """Returns a leaderboard of the groups with the most links added to them!"""
        if number_of_entries > 50:
            number_of_entries = 50
        async with ctx.channel.typing():
            lb = get_group_leaderboard(number_of_entries)
            one_str = ""
            for i, pair in enumerate(lb, start=1):
                if str(i).endswith('1') and i != 11:
                    suffix = 'st.'
                elif str(i).endswith('2') and i != 12:
                    suffix = 'nd.'
                elif str(i).endswith('3') and i != 13:
                    suffix = 'rd.'
                else:
                    suffix = 'th.'
                name = pair[0].title()
                link_count = pair[1]
                spacing = 40 - len(str(i) + suffix + name)
                elem = f"`{i}{suffix} {name}{' ' * spacing}{link_count}`\n"
                one_str = one_str + elem
            embed = discord.Embed(title="Group Leaderboard",
                                  description=one_str,
                                  color=discord.Color.blurple())
            await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Levels(disclient))
