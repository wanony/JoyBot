import concurrent.futures

import nextcord as discord
import os
from nextcord.ext import commands
from data import apis_dict, add_guild_db, write_cache

# intents = discord.Intents(members=True, guilds=True, presences=True)
intents = discord.Intents(presences=True)

executor = concurrent.futures.ThreadPoolExecutor()

joy_guild = 741066661221761135  # set to joy guild ID

disclient = commands.Bot(
    intents=intents,
)  # , intents=intents)
disclient.remove_command('help')
# commands.DefaultHelpCommand(width=100, dm_help=True, dm_help_threshold=100)


@disclient.event
async def on_ready():
    await disclient.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="for Slash Commands!"),
        status=discord.Status.online
    )
    print(f"bot is online as {disclient.user.name} in {len(disclient.guilds)} guilds!:")
    for guild in disclient.guilds:
        # add if guild id not in guild table here...
        added = add_guild_db(guild.id)
        if added:
            print(f'Added {guild.name} with {guild.member_count} members to the database!\n(ID: {guild.id})')
        else:
            print(f'{guild.name}: Member Count: {guild.member_count}\n(ID: {guild.id})')

    await disclient.loop.create_task(write_cache())


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

try:
    disclient.run(apis_dict["discord_token"])
finally:
    executor.shutdown()
    disclient.close()
