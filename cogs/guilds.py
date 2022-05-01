import re

import nextcord as discord
from nextcord.ext import commands

from data import remove_restricted_user, add_restricted_user, set_guild_max_timer_db
from embeds import error_embed, success_embed


class Server(commands.Cog):
    """Server specific commands.
    """
    def __init__(self, disclient):
        self.disclient = disclient

    @discord.slash_command(
        name='setmaxtimer',
        description='set the maximum timer duration in this server'
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def _set_max_timer(self, interaction: discord.Interaction, timer_limit):
        """Set a timer limit for `timer` commands used in this server!
        Example:
        .set_max_timer 10"""
        guild_id = interaction.guild.id
        set_limit = set_guild_max_timer_db(timer_limit, guild_id)
        if set_limit:
            await interaction.response.send_message(
                embed=success_embed(f'Set the timer limit to `{timer_limit}` minute(s) in {interaction.guild.name}!'),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=error_embed(f'Failed to set the timer limit!'), ephemeral=True)

    @discord.slash_command(
        name="restrictuser",
        description="make a user unable to use Joy in this server"
    )
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def _restrict_user(self, interaction: discord.Interaction, member: discord.Member):
        """Restricts a user from using Joy's Fun category commands in this discord.
        The user can continue to use the bot in DMs, other categories, and in other discords."""
        added = add_restricted_user(interaction.guild_id, member.id)
        if added:
            await interaction.response.send_message(
                embed=success_embed(f'Restricted {member} in {interaction.guild.name}!'), ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=error_embed(f'{member} is already restricted in {interaction.guild.name}!'), ephemeral=True)

    @discord.slash_command(
        name='unrestrictuser',
        description='unrestrict a user in your server'
    )
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def _unrestrict_user(self, interaction: discord.Interaction, member: discord.Member):
        """Unrestricts a user from using Joy's Fun category commands in this discord."""
        removed = remove_restricted_user(interaction.guild.id, member.id)
        if removed:
            await interaction.response.send_message(
                embed=success_embed(f'{member} is no longer restricted in {interaction.guild.name}!'))
        else:
            await interaction.response.send_message(
                embed=error_embed(f'{member} is not restricted in {interaction.guild.name}!'))


def setup(disclient):
    disclient.add_cog(Server(disclient))
