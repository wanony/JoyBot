# import discord
from discord.ext import commands
import json
import asyncio
from data import custom_dict
from data import direc_dict


class Custom(commands.Cog):
    """This category contains commands that can be made
    by users that are for fun, such a their own memes or
    reaction gfys or youtube links.
    """
    def __init__(self, disclient):
        self.disclient = disclient
        self.disclient.loop.create_task(self.write_custom())

    @commands.Cog.listener()
    async def write_custom(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["custom"], 'w') as cus:
                json.dump(custom_dict, cus, indent=4)
            await asyncio.sleep(5)

    @commands.command(aliases=['delcommand', 'dc'])
    @commands.has_any_role('Moderator', 'Admin')
    async def delete_command(self, ctx, command):
        """MOD: Removes a custom command created previously"""
        command = command.lower()
        if command in custom_dict["command_list"]:
            custom_dict["command_list"].remove(command)
            com_dict = custom_dict["commands"]
            del com_dict[command]
            await ctx.send("Custom command: `" + command + "` removed.")

    @commands.command(aliases=['commands'])
    async def command_list(self, ctx):
        """Sends a list of all the custom commands"""
        arrr = custom_dict["command_list"]
        await ctx.send(f"`{format_list(arrr)}`")

    @commands.command(aliases=['ac', 'addcommand'])
    async def add_command(self, ctx, name, gfy):
        """
        Adds a custom command with a valid gfy/red/gif link!
        Example: .addcommand fun <link>
        You can now call this command with .fun
        """
        name = name.lower()
        valid = (
            "https://gfycat.com/",
            "https://www.youtube.com/",
            "https://redgifs.com/",
            "https://www.gifdeliverynetwork.com/"
        )
        if name in custom_dict["command_list"]:
            await ctx.send(
                "Command name already exists! Try a different name.")
        elif "." in name:
            await ctx.send("Illegal character `.` in command name!")
        elif gfy.startswith(valid):
            custom_dict["command_list"].append(name)
            new_command = {name: gfy}
            custom_dict["commands"].update(new_command)
            await ctx.send(f"Command: `.{name}` added!")
        else:
            await ctx.send(
                "Link invalid, use gfycat, redgifs, gifdeliverynet or youtube")


def format_list(array):
    formatted = '`, `'.join(array)
    return formatted


def setup(disclient):
    disclient.add_cog(Custom(disclient))
