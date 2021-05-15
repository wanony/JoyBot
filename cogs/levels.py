import discord
from discord.ext import commands
import json
import asyncio
from data import direc_dict
from data import users
from data import contri_dict


class Levels(commands.Cog):
    """Levels, XP, and contribution handling commands found here
    will let users get information about levels and leaderboards
    of the top contributors!
    """
    def __init__(self, disclient):
        self.disclient = disclient
        self.disclient.loop.create_task(self.write_people())

    @commands.Cog.listener()
    async def write_people(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["levels"], 'w') as lev:
                json.dump(users, lev, indent=4)
            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.disclient.user:
            return
        if message.author.bot:
            return
        author = str(message.author.id)
        if author not in users:
            users[author] = {}
            users[author]['level'] = 1
            users[author]['xp'] = 0
        users[author]['xp'] += 1
        if self.level_up(author):
            embed = discord.Embed(colour=message.author.colour,
                                  title="Level Up!!")
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.add_field(name="Level:", value=users[author]['level'])
            embed.add_field(name="XP:", value=users[author]['xp'])
            await message.channel.send(embed=embed)

    def level_up(self, author):
        current_xp = users[author]['xp']
        current_lvl = users[author]['level']
        if current_xp >= current_lvl * 100:
            users[author]['level'] += 1

    @commands.command(aliases=['xp'])
    async def level(self, ctx, member: discord.Member = None):
        """Returns information of the users level"""
        if member:
            member = member
        else:
            member = ctx.author
        if str(member.id) in users:
            embed = discord.Embed(colour=member.colour, title="Level & XP")
            embed.set_author(name=member)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}",
                             icon_url=ctx.author.avatar_url)
            embed.add_field(name="Level:",
                            value=users[str(member.id)]['level'])
            embed.add_field(name="XP:", value=users[str(member.id)]['xp'])
            await ctx.send(embed=embed)
        else:
            await ctx.send("Member has no XP!")

    @commands.command()
    async def leaderboard(self, ctx):
        """
        Returns a leaderboard of the top 10 contributers!
        This leaderboard is made from all contributers across
        every server the bot is connected to.
        """
        leads = []
        for usr in contri_dict:
            leads.append((contri_dict[usr]["cont"], await self.disclient.fetch_user(usr)))
        leads.sort(reverse=True)
        embed = discord.Embed(title="Contribution Leaderboard",
                              description="",
                              color=discord.Color.blurple())
        for idx, pair in enumerate(leads[:10], start=1):
            name = pair[1].name + '#' + pair[1].discriminator
            elem = f"`{idx}. {name}{' ' * (29 - len(name))}{pair[0]}`"
            embed.add_field(name="-", value=elem, inline=False)
        await ctx.send(embed=embed)


def format_list(array):
    formatted = ''.join(array)
    return formatted


def setup(disclient):
    disclient.add_cog(Levels(disclient))
