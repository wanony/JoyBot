import discord
import os
from discord.ext import commands
from data import apis_dict, add_guild_db
from data import default_prefix
from data import get_prefix_db

intents = discord.Intents.default()
intents.members = True


def get_prefix(disclient, message):
    guild = message.guild
    if guild:
        prefix = get_prefix_db(guild.id)
        if prefix:
            return prefix
        else:
            return default_prefix
    else:
        return default_prefix


disclient = commands.Bot(
    intents=intents,
    command_prefix=get_prefix
)  # , intents=intents)
disclient.remove_command('help')
# commands.DefaultHelpCommand(width=100, dm_help=True, dm_help_threshold=100)


@disclient.event
async def on_ready():
    await disclient.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for .help"),
                                    status=discord.Status.online)
    print(f"bot is online as {disclient.user.name} in {len(disclient.guilds)} guilds!:")
    for guild in disclient.guilds:
        # add if guild id not in guild table here...
        added = add_guild_db(guild.id)
        if added:
            print(f'Added {guild.name} to the database! (ID: {guild.id})')
        else:
            print(f'{guild.name}: (ID: {guild.id})')


try:
    for cog in os.listdir("./cogs"):
        if cog.endswith(".py"):
            try:
                cog = f"cogs.{cog.replace('.py', '')}"
                disclient.load_extension(cog)
                print(cog)
            except commands.ExtensionNotLoaded:
                print(f"Failed to load {cog}")
except OSError:
    print("No cogs to load!")


disclient.run(apis_dict["discord_token"])
