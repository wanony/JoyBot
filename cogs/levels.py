import nextcord as discord
from nextcord import SlashOption
from nextcord.ext import commands
from data import find_user, add_user, add_user_xp, get_idol_leaderboard, get_group_leaderboard
from data import get_leaderboard


class Levels(commands.Cog):
    """Levels, XP, and contribution commands found here
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient

    @discord.slash_command(
        name="leaderboard",
        description="see some top statistics!"
    )
    async def leaderboard(self,
                          interaction: discord.Interaction,
                          option: str = SlashOption(
                              name="option",
                              description="what leaderboard to view",
                              required=True
                          ),
                          number: str = SlashOption(
                              name="number",
                              description="size of leaderboard to display",
                              required=False
                          )):
        """Returns a leaderboard of the top 10 contributers!
        This leaderboard is made from all contributers across
        every server the bot is connected to.
        """
        # TODO remove duplicate code harder
        if number:
            number = int(number)
        else:
            number = 10
        if option.lower() == "contribution":
            lb = get_leaderboard(number)
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
            await interaction.response.send_message(embed=embed)
        elif option.lower() == "idols":
            lb = get_idol_leaderboard(number)
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
            await interaction.response.send_message(embed=embed)
        elif option.lower() == "groups":
            lb = get_group_leaderboard(number)
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
            await interaction.response.send_message(embed=embed)

    @leaderboard.on_autocomplete("number")
    async def _leaderboard_helper(self, interaction: discord.Interaction, number: str):
        if not number:
            await interaction.response.send_autocomplete(["10", "25"])
            return
        get_near_choice = [n for n in ["10", "25"] if n.lower().startswith(number.lower())]
        await interaction.response.send_autocomplete(get_near_choice)

    @leaderboard.on_autocomplete("option")
    async def _leaderboard_option(self, interaction: discord.Interaction, option: str):
        options = ["contribution", "idols", "groups"]
        if not option:
            await interaction.response.send_autocomplete(options)
            return
        get_near_option = [o for o in options if o.startswith(option.lower())]
        await interaction.response.send_autocomplete(get_near_option)


def setup(disclient):
    disclient.add_cog(Levels(disclient))
