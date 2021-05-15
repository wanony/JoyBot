import discord
import asyncio
import json
from discord.ext import commands
from data import mods_dict
from data import auditing_dict
from data import gfys_dict
from data import direc_dict


def check_user_is_mod(ctx):
    if ctx.author.id in mods_dict["mods"] or check_user_is_owner(ctx):
        return True
    else:
        return False


def check_user_is_owner(ctx):
    if ctx.author.id in mods_dict["owners"]:
        return True
    else:
        return False


class Owner(commands.Cog):
    """Commands for owner usage."""
    def __init__(self, disclient):
        self.disclient = disclient

    @commands.command()
    async def remove_moderator(self, ctx, member: discord.Member):
        """add user to moderator list."""
        if not check_user_is_owner(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        if member.id in mods_dict["mods"]:
            mods_dict["mods"].remove(member.id)
            embed = discord.Embed(title='Success!',
                                  description=f'{member} removed from the moderator list!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Error!',
                                  description=f'{member} is not a moderator!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command()
    async def add_moderator(self, ctx, member: discord.Member):
        """add user to moderator list."""
        if not check_user_is_owner(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        if member.id not in mods_dict["mods"]:
            mods_dict["mods"].append(member.id)
            embed = discord.Embed(title='Success!',
                                  description=f'{member} added to moderator list!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Error!',
                                  description=f'{member} is already a moderator!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)


class Moderation(commands.Cog):
    """Commands for moderators.
    """
    def __init__(self, disclient):
        self.disclient = disclient
        self.disclient.loop.create_task(self.write_auditing())
        self.disclient.loop.create_task(self.write_mods())

    @commands.Cog.listener()
    async def write_auditing(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["auditing"], 'w') as audd:
                json.dump(auditing_dict, audd, indent=4)
            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def write_mods(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["mods"], 'w') as modd:
                json.dump(mods_dict, modd, indent=4)
            await asyncio.sleep(5)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="None!"):
        """Kicks a member"""
        await member.kick(reason=reason)
        await ctx.send(
                    f"{member.mention} kicked by {ctx.author} for: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="None!"):
        """Bans a member"""
        await member.ban(reason=reason)
        await ctx.send(
                    f"{member.mention} banned by {ctx.author} for: {reason}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, number: int):
        """
        Deletes a specified number of messages in the channel
        the command is invoked in
        """
        channel = ctx.channel
        await channel.purge(limit=number+1)
        if number == 1:
            msg = "Cleared 1 message!"
        else:
            msg = f"Cleared `{number}` messages!"
        embed = discord.Embed(title="Success!",
                              description=msg,
                              color=discord.Color.green())
        await ctx.send(embed=embed)

    # --- Commands to moderate content --- #

    @commands.command(aliases=['addgroups'])
    async def addgroup(self, ctx, *args):
        """Adds a group"""
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        group_list = args
        if not group_list:
            await ctx.send("No group arguement(s) given.")
        else:
            for groups in group_list:
                if groups in gfys_dict["groups"]:
                    await ctx.send("Group `" + groups + "` already exists.")
                else:
                    updater = {str(groups).lower(): {}}
                    gfys_dict["groups"].update(updater)
                    await ctx.send("Added group `" + groups + "`!")

    @commands.command(aliases=['addidol'])
    async def addidols(self, ctx, group, *args):
        """Adds an idol to an already existing group"""
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        group = group.lower()
        idol_list = args
        if not group:
            await ctx.send("No group arguement given.")
        elif group.lower() not in gfys_dict["groups"]:
            await ctx.send(
                "Group doesn't exist, create the group first with `.addgroup`")
        else:
            if not idol_list:
                await ctx.send("No idol(s) provided.")
            else:
                for idol in idol_list:
                    idol = idol.lower()
                    sub_dict = gfys_dict["groups"][group]
                    if idol in sub_dict:
                        await ctx.send(
                            f"`{idol.title()}` already in `{group}`.")
                    else:
                        updater = {idol: []}
                        sub_dict.update(updater)
                        await ctx.send(f"Added `{idol.title()}` to `{group}`.")

    @commands.command(aliases=['removetag'])
    async def remove_tag(self, ctx, link, *tags):
        """
        Removes tag(s) from a link previously added
        Example: <link> <tag> <tag> <tag>
        Any number of tags can be removed in one command.
        """
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        tags_list = tags
        for tag in tags_list:
            tag = tag.lower()
            if link in gfys_dict["tags"][tag]:
                gfys_dict["tags"][tag].remove(link)
                await ctx.send(f"Removed `{tag}` from the link!")
            else:
                await ctx.send(f"Gfy doesn't have `{tag}`!")

    @commands.command(aliases=['deletetag', 'deltag'])
    async def delete_tag(self, ctx, tag):
        """
        Completely deletes a tag
        All links with this tag, will no longer have this tag
        """
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        tag = tag.lower()
        if tag in gfys_dict["tags"]:
            if tag in gfys_dict["grave"]:
                tag = tag + "(copy)"
            grave = gfys_dict["grave"]
            updater = {tag: gfys_dict["tags"][tag]}
            grave.update(updater)
            del gfys_dict["tags"][tag]
            await ctx.send(f"Deleted tag: `{tag}`.")
        else:
            await ctx.send(f"No tag: `{tag}`.")

    @commands.command(aliases=['delfancam'])
    async def delete_fancam(self, ctx, group, idol, *links):
        """
        Deletes a fancam link from the specified idol
        Example: .delete_fancam <group> <idol> <fancam_link>
        """
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        group = group.lower()
        idol = idol.lower()
        for link in links:
            if link.startswith("https://www.youtu"):
                if link in gfys_dict["groups"][group][idol]:
                    gfys_dict["groups"][group][idol].remove(link)
                    await ctx.send(f"Removed link from {idol}")
                else:
                    await ctx.send(f"Link not in `{group} {idol}`")
            else:
                await ctx.send("Link is not valid")

    @commands.command(aliases=['delimage'])
    async def delete_image(self, ctx, group, idol, *links):
        """
        Deletes an image link from the specified idol
        Example .delete_image <group> <idol> <image_link>
        """
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        group = group.lower()
        idol = idol.lower()
        for link in links:
            fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
            if link.endswith(fts):
                if link in gfys_dict["groups"][group][idol]:
                    gfys_dict["groups"][group][idol].remove(link)
                    await ctx.send(f"Removed link from {idol}")
                else:
                    await ctx.send(f"Link not in `{group} {idol}`")
            elif link.startswith("https://pbs.twimg"):
                if link in gfys_dict["groups"][group][idol]:
                    gfys_dict["groups"][group][idol].remove(link)
                    await ctx.send(f"Removed link from {idol}")
                else:
                    await ctx.send(f"Link not in `{group} {idol}`")
            else:
                await ctx.send("Link is not valid")

    @commands.command(aliases=['delgfy'])
    async def delete_gfy(self, ctx, group, idol, *links):
        """
        Deletes a gfy from the specified idol
        Example: .delete_gfy <group> <idol> <gfy_link>
        """
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        group = group.lower()
        idol = idol.lower()
        for link in links:
            if group in gfys_dict["groups"]:
                group_dict = gfys_dict["groups"][group]
                if idol in group_dict:
                    if link in group_dict[idol]:
                        group_dict[idol].remove(link)
                        await ctx.send(
                            "Removed gfy from `" + idol.title() + "`!")
                    else:
                        await ctx.send(
                            f"No link matching `{idol.title()}` in `{group}`.")
                else:
                    await ctx.send(
                        f"No content for `{idol.title()}` in `{group}`")
            else:
                await ctx.send(f"No group named `{group}`.")

    @commands.command(aliases=['delgroup'])
    async def delete_group(self, ctx, group):
        """
        Deletes an entire group and all idols within
        Example: .delete_group <group>
        """
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        group = group.lower()
        if group in gfys_dict["groups"]:
            grave = gfys_dict["grave"]
            updater = {group: gfys_dict["groups"][group]}
            grave.update(updater)
            del gfys_dict["groups"][group]
            await ctx.send("Deleted group `" + group + "`.")
        else:
            await ctx.send("Group doesn't exist!")

    @commands.command(aliases=['delidol', 'delidols'])
    async def delete_idols(self, ctx, group, *args):
        """
        Deletes all idol(s) specified in a group
        Example: .delete_idols <group> <idol_1> <idol_2>
        """
        if not check_user_is_mod(ctx):
            embed = discord.Embed(title='Error!',
                                  description='Permission denied!',
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        group = group.lower()
        idol_list = args
        if group.lower() not in gfys_dict["groups"]:
            await ctx.send(
                "Group doesn't exist, create the group first with `.addgroup`")
        else:
            if not idol_list:
                await ctx.send("No idol(s) provided.")
            else:
                for idol in idol_list:
                    idol = idol.lower()
                    sub_dict = gfys_dict["groups"][group]
                    if idol in sub_dict:
                        grave = gfys_dict["grave"]
                        updater = {idol: gfys_dict["groups"][group][idol]}
                        grave.update(updater)
                        del sub_dict[idol]
                        await ctx.send(
                            f"Removed `{idol.title()}` from `{group}`")
                    else:
                        await ctx.send(f"No `{idol.title()}` in `{group}`")

    @commands.command(aliases=['addauditing'])
    async def add_auditing(self, ctx):
        """Adds auditing from this channel, as links are added to
        the bot, they will also be posted here so all new additions
        can be viewed."""
        if ctx.channel.id not in auditing_dict["auditing_channels"]:
            auditing_dict["auditing_channels"].append(ctx.channel.id)
            des = 'Added this channel to the auditing list!'
            embed = discord.Embed(title='Success!',
                                  description=des,
                                  color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            des = 'Channel already in auditing list!'
            embed = discord.Embed(title='Error!',
                                  description=des,
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(aliases=['removeauditing'])
    async def remove_auditing(self, ctx):
        """Removes auditing from this channel!"""
        if ctx.channel.id in auditing_dict["auditing_channels"]:
            auditing_dict["auditing_channels"].remove(ctx.channel.id)
            des = 'Removed this channel from the auditing list!'
            embed = discord.Embed(title='Success!',
                                  description=des,
                                  color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            des = 'Channel not in the auditing list!'
            embed = discord.Embed(title='Error!',
                                  description=des,
                                  color=discord.Color.red())
            await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Moderation(disclient))
    disclient.add_cog(Owner(disclient))
