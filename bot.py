import discord
import datetime
import shutil
import threading
import os
from discord.ext import commands
from data import direc_dict
from data import apis_dict
from data import command_prefix

intents = discord.Intents.default()
intents.members = True

disclient = commands.Bot(
    intents=intents,
    command_prefix=command_prefix,
)  # , intents=intents)
# for when it comes for a custom help command
disclient.remove_command('help')
# commands.DefaultHelpCommand(width=100, dm_help=True, dm_help_threshold=100)


@disclient.event
async def on_ready():
    await disclient.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for .help"),
                                    status=discord.Status.online)
    print(f"bot is online as {disclient.user.name} in:")
    for guild in disclient.guilds:
        print(f'{guild.name}: (ID: {guild.id})')


def backup_gfy_file():
    shutil.copyfile(direc_dict["gfys"], './backupgfys/backupgfys.json')
    print("gfys backed up at " + str(datetime.datetime.now()))
    threading.Timer(3600.0, backup_gfy_file).start()


def backup_users_file():
    shutil.copyfile(direc_dict["levels"], './backupgfys/backuplvls.json')
    print("users backed up at " + str(datetime.datetime.now()))
    threading.Timer(3600.0, backup_users_file).start()


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


backup_gfy_file()
backup_users_file()
disclient.run(apis_dict["discord_token"])
