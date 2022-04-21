import nextcord as discord
from nextcord import SlashOption
from nextcord.ext import commands
from data import find_user, check_user_is_mod
from data import apis_dict
from embeds import success_embed, thanks_embed
from data import default_prefix


class General(commands.Cog):
    """General commands that are useful to get information about users or help!
    """

    def __init__(self, disclient):
        self.disclient = disclient

    # TODO fix the help command
    @discord.slash_command(name='help',
                           description="Get help regarding commands or command groups",
                           guild_ids=[755143761922883584])
    async def help(
            self, interaction: discord.Interaction,
            category: str = SlashOption(
                name="category",
                description="Chose a command category",
                required=False),
            command: str = SlashOption(
                name="command",
                description="Chose a command",
                required=False)
    ):
        """Gets all categories and commands of the bot."""
        if not category and not command:
            titl = 'Category List'
            desc = f"Use `{default_prefix}help <Category>` to find out more about them! \n"
            halp = discord.Embed(title=titl,
                                 description=desc,
                                 color=discord.Color.blurple())
            cogs_desc = ''
            if not check_user_is_mod(interaction):
                for name, cog in self.disclient.cogs.items():
                    if name != 'Events' and name != 'Owner' and name != 'Moderation':
                        cogs_desc = cogs_desc + f'`{name}` - {cog.__doc__}\n'
            else:
                for name, cog in self.disclient.cogs.items():
                    if name != 'Events' and name != 'Owner':
                        cogs_desc = cogs_desc + f'`{name}` - {cog.__doc__}\n'
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
            await interaction.response.send_message(embed=halp, ephemeral=True)
        else:
            # Don't process dumb amounts of input
            if len(args) > 5:
                errr = "Too many categories given!"
                halp = discord.Embed(title='Error!',
                                     description=errr,
                                     color=discord.Color.red())
                await interaction.message.add_reaction(emoji='✉')
                await interaction.message.author.send(embed=halp)
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
                        # if just command, send to channel
                        halp = discord.Embed(title=command.name,
                                             description=f"{command.help}\n\nAliases: {', '.join(command.aliases)}",
                                             color=discord.Color.blurple())
                        await interaction.send(embed=halp)
                        return
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
                await interaction.message.add_reaction(emoji='✉')
                await interaction.message.author.send(embed=halp)

    def category_helper(self, interaction: discord.Interaction):
        if not check_user_is_mod(interaction):
            return [
                category for category in self.disclient.cogs
                if category != 'Events' and category != 'Owner' and category != 'Moderation'
            ]
        else:
            return [
                category for category in self.disclient.cogs
                if category != 'Events' and category != 'Owner'
            ]

    @help.on_autocomplete("category")
    async def _category(self, interaction: discord.Interaction, category_name):
        if not category_name:
            await interaction.response.send_autocomplete(self.category_helper(interaction)[:25])
            return

        get_near_categories = [cat for cat in self.category_helper(interaction)
                               if cat.lower().startswith(category_name.lower())]
        await interaction.response.send_autocomplete(get_near_categories[:25])

    @help.on_autocomplete("command")
    async def _command(self, interaction: discord.Interaction, command_name):
        if not command_name:
            await interaction.response.send_autocomplete(self.disclient.commands[:25])
            return
        get_near_groups = [command for command in self.disclient.commands if
                           command.lower().startswith(command_name.lower())]
        await interaction.response.send_autocomplete(get_near_groups[:25])

    @discord.slash_command(name='avatar',
                           description="See a larger version of a user avatar",
                           guild_ids=[755143761922883584, 783047562655301653])
    async def get_avatar(self, interaction: discord.Interaction,
                         member: discord.Member = SlashOption(name="user",
                                                              description="Select a user",
                                                              required=False),
                         ):
        """Returns the users' avatar."""
        if member:
            member = member
        else:
            member = interaction.user
        embed = discord.Embed(colour=member.colour)
        embed.set_author(name=member)
        embed.set_footer(text=f"requested by {interaction.user.name}",
                         icon_url=interaction.user.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @discord.slash_command(
        name="profile",
        description="Get some user information"
    )
    async def user_profile(self,
                           interaction: discord.Interaction,
                           member: discord.Member = SlashOption(
                               name="user",
                               description="select a user",
                               required=False
                           )):
        if member:
            member = member
        else:
            member = interaction.user
        user = find_user(member.id)
        cont = user[2]
        cr_at = member.created_at.strftime("%a, %#d %B %Y, %I:%M%p UTC")
        jo_at = member.joined_at.strftime("%a, %#d %B %Y, %I:%M%p UTC")
        embed = discord.Embed(colour=member.colour)
        embed.set_author(name=member)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}",
                         icon_url=interaction.user.avatar.url)
        # Set level system purely based on contribution, make contribution more in-depth
        embed.add_field(name="Contribution:", value=cont)
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Account Created:", value=cr_at)
        if interaction.guild:
            embed.add_field(name="Joined Server:", value=jo_at)
        await interaction.response.send_message(embed=embed)

    @discord.slash_command(
        name="report",
        description="report a link on Joy",
        guild_ids=[755143761922883584]
    )
    async def report(self,
                     interaction: discord.Interaction,
                     link: str = SlashOption(
                         name="link",
                         description="provide the link to report",
                         required=True
                     ),
                     reason: str = SlashOption(
                         name="reason",
                         description="the reason for reporting this link",
                         required=True
                     )):
        """If you see something you think doesn't belong on the bot, report it
        Usage: .report <link> <reason>
        The reason can be as long as you need it to be."""
        author = interaction.user
        embed = discord.Embed(title='Link Reported!',
                              description=f'Reason: {reason}\n\n{link}',
                              color=discord.Color.orange())
        embed.set_footer(text=f"Reported by {author}",
                         icon_url=author.avatar.url)
        report_chan = self.disclient.get_channel(apis_dict["reporting_channel"])
        await report_chan.send(embed=embed)
        await interaction.response.send_message(embed=success_embed('Link reported!'), ephemeral=True)

    @discord.slash_command(
        name="suggest",
        description="suggest a new feature for Joy",
        guild_ids=[755143761922883584]
    )
    async def suggestion(self,
                         interaction: discord.Interaction,
                         suggestion: str = SlashOption(
                             name="suggestion",
                             description="provide your suggestion!",
                             required=True
                         ),
                         anonimity: str = SlashOption(
                             name="anonimity",
                             description="Do you to suggest anonymously?",
                             required=True
                         )):
        """Make a suggestion for the improvement of Joy as a discord bot!"""
        anonimity = True if anonimity.lower() == "yes" else False
        suggestion_channel = self.disclient.get_channel(apis_dict['suggestion_channel'])
        embed = discord.Embed(title='Suggestion!',
                              description=suggestion,
                              color=discord.Color.blurple())
        if not anonimity:
            embed.set_footer(text=f"Suggested by {interaction.user}",
                             icon_url=interaction.user.avatar.url)
        await suggestion_channel.send(embed=embed)
        if not anonimity:
            msg = 'Your suggestion has been recorded and it will be looked at as soon as possible!'
        else:
            msg = 'Your suggestion has been recorded anonymously and will be looked at as soon as possible'
        await interaction.response.send_message(embed=thanks_embed(msg))

    @suggestion.on_autocomplete("anonimity")
    async def _anon_helper(self, interaction: discord.Interaction, choice: str):
        if not choice:
            await interaction.response.send_autocomplete(["yes", "no"])
            return
        get_near_choice = [choice for choice in ["yes", "no"] if choice.lower().startswith(choice.lower())]
        await interaction.response.send_autocomplete(get_near_choice)


def setup(disclient):
    disclient.add_cog(General(disclient))
