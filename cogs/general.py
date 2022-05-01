import nextcord as discord
from nextcord import SlashOption
from nextcord.ext import commands
from data import find_user
from data import apis_dict
from embeds import success_embed, thanks_embed


class General(commands.Cog):
    """General commands that are useful to get information about users or help!
    """

    def __init__(self, disclient):
        self.disclient = disclient

    @discord.slash_command(name='avatar',
                           description="See a larger version of a user avatar")
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
        description="report a link on Joy"
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
        description="suggest a new feature for Joy"
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
