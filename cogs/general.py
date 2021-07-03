import discord
from discord.ext import commands
from data import find_user, check_user_is_mod, check_user_is_owner


class General(commands.Cog):
    """General commands that are useful to get
    information about users or help!
    """
    def __init__(self, disclient):
        self.disclient = disclient

    @commands.command(pass_context=True)
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def help(self, ctx, *args):
        """Gets all categories and commands of the bot."""
        if not args:
            titl = 'Category List'
            desc = 'Use `.help <Category>` to find out more about them! \n'
            halp = discord.Embed(title=titl,
                                 description=desc,
                                 color=discord.Color.blurple())
            cogs_desc = "\n".join(
                [f'`{name}` - {cog.__doc__}'
                 for name, cog in self.disclient.cogs.items()]
            )
            halp.add_field(name='Categories',
                           value=cogs_desc,
                           inline=False)
            cmds_desc = "\n".join(
                [f'`{y.name}` - {y.help}'
                 for y in self.disclient.walk_commands()
                 if not y.cog_name and not y.hidden]
            )
            if len(cmds_desc) > 0:
                halp.add_field(name='Uncatergorized Commands',
                               value=cmds_desc,
                               inline=False)
            await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send(embed=halp)
        else:
            # Don't process dumb amounts of input
            if len(args) > 5:
                errr = "Too many categories given!"
                halp = discord.Embed(title='Error!',
                                     description=errr,
                                     color=discord.Color.red())
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send(embed=halp)
                return

            for arg in set(args):
                # Check standard capitalized format first
                cog = None
                if arg.capitalize() in self.disclient.cogs:
                    cog = self.disclient.cogs[arg.capitalize()]
                elif arg in self.disclient.cogs:
                    # Attempt to use raw input on fallback
                    cog = self.disclient.cogs[arg]

                if cog is None:
                    # Check if it is a command
                    command = None
                    for c in self.disclient.walk_commands():
                        if arg.lower() == c.name.lower():
                            command = c

                    if command:
                        halp = discord.Embed(title=command.name,
                                             description=command.help,
                                             color=discord.Color.blurple())
                    else:
                        errr = f"Category '{arg}' not found!"
                        halp = discord.Embed(title='Error!',
                                             description=errr,
                                             color=discord.Color.red())
                else:
                    titl = f"{arg.capitalize()} Command List"
                    halp = discord.Embed(title=titl,
                                         description=cog.__doc__,
                                         color=discord.Color.blurple())
                    for c in cog.get_commands():
                        if not c.hidden:
                            halp.add_field(name=c.name,
                                           value=c.help,
                                           inline=False)
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send(embed=halp)

    @commands.command(aliases=['avatar'])
    async def get_avatar(self, ctx, member: discord.Member = None):
        """returns the users avatar"""
        if member:
            member = member
        else:
            member = ctx.author
        embed = discord.Embed(colour=member.colour)
        embed.set_author(name=member)
        embed.set_footer(text=f"requested by {ctx.author}",
                         icon_url=ctx.author.avatar_url)
        embed.set_image(url=member.avatar_url_as(size=512))
        await ctx.send(embed=embed)

    @commands.command(aliases=['profile'])
    async def user_profile(self, ctx, member: discord.Member = None):
        """returns some user information"""
        if member:
            member = member
        else:
            member = ctx.author
        print(member)
        user = find_user(member.id)
        xp = user[1]
        cont = user[2]
        cr_at = member.created_at.strftime("%a, %#d %B %Y, %I:%M%p UTC")
        jo_at = member.joined_at.strftime("%a, %#d %B %Y, %I:%M%p UTC")
        embed = discord.Embed(colour=member.colour)
        embed.set_author(name=member)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}",
                         icon_url=ctx.author.avatar_url)
        # need better level system
        embed.add_field(name="Level:", value=xp // 100)
        embed.add_field(name="XP:", value=xp)
        embed.add_field(name="Contribution:", value=cont)
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Account Created:", value=cr_at)
        embed.add_field(name="Joined Server:", value=jo_at)
        await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(General(disclient))
