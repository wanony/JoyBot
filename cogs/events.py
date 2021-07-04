from discord.ext import commands
from data import command_prefix
from data import get_commands


class Events(commands.Cog):
    """Events that handle user errors and messages.
    No user commands added here... Yet.
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient

    @commands.Cog.listener()
    @commands.has_permissions(manage_messages=True)
    async def on_message(self, message):
        if message.author == self.disclient.user:
            return
        # user = message.author
        msg = message.content.split(" ")
        if msg[0].startswith(command_prefix):
            command = msg[0][1:]
            command_list = get_commands()
            if command in command_list:
                await message.channel.send(command_list[command])

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Permission denied!")
            raise error
        if isinstance(error, commands.CommandNotFound):
            async for message in ctx.history(limit=1):
                if message.author == self.disclient.user:
                    print("sent out a custom command")
                else:
                    print("Command not found!")
                    raise error


def setup(disclient):
    disclient.add_cog(Events(disclient))
