import discord
from discord.ext import commands
from random import SystemRandom
import asyncio
from datetime import datetime
from embeds import error_embed, warning_embed

# import lots of shit from datafile.
from data import find_group_id, get_member_links_with_tag, get_member_links, find_member_id, get_all_alias_of_tag
from data import find_member_aliases, find_group_id_and_name, get_group_aliases, find_member_id_and_name
from data import get_tag_parent_from_alias, get_all_tag_names, add_tag, find_tag_id, add_tag_alias, add_link_tags
from data import add_link, get_link_id, add_link_to_member, find_user, add_user_contribution, add_user
from data import random_link_from_links, member_link_count, get_links_with_tag, get_groups
from data import get_members_of_group_and_link_count, count_links_of_member, get_all_tags_on_member_and_count
from data import last_three_links, count_links, apis_dict, get_auditing_channels, remove_auditing_channel


class Fun(commands.Cog):
    """All of the commands listed here are for gfys, images, or fancams.
    All groups with multiple word names are written as one word.
    Example: Red Velvet will become RedVelvet
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        self.loops = {}  # dict for timers
        self.recent_dict = {}
        # self.disclient.loop.create_task(self.write_recent())

    # @commands.Cog.listener()
    # async def write_recent(self):
    #     await self.disclient.wait_until_ready()
    #     while not self.disclient.is_closed():
    #         with open(direc_dict["recents"], 'w') as rece:
    #             json.dump(recent_dict, rece, indent=4)
    #         await asyncio.sleep(5)
    @commands.command()
    async def image(self, ctx, group, idol, *tags):
        """
        Sends an image from a specified group and idol
        Example: .image <group> <idol>
        This can be invoked with tags following <idol>
        Example .image <group> <idol> <tag> <tag>
        """
        group = group.lower()
        idol = idol.lower()
        g_id = find_group_id(group)
        if not g_id:
            await ctx.send(embed=error_embed(f'No group added named {group}!'))
            return
        m_id = find_member_id(g_id[0], idol)
        if not m_id:
            await ctx.send(embed=error_embed(f'No idol named {idol} in {group}!'))
            return
        link_list = []
        no_tag = []
        if tags:
            for tag in tags:
                tag = tag.lower()
                # rework sql to take a list of tags at once, rather than multiple
                # https://stackoverflow.com/questions/589284/imploding-a-list-for-use-in-a-python-mysqldb-in-clause
                tagged_links = get_member_links_with_tag(m_id[0], tag)
                if tagged_links:
                    link_list.extend([x[0] for x in tagged_links])
                else:
                    no_tag.append(tag)
        if not link_list:
            links = get_member_links(m_id[0])
            if links:
                link_list.extend([x[0] for x in links])
            else:
                await ctx.send(embed=error_embed(f"No content for `{idol.title()}` in `{group}`!"))
                return
        fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
        link_list = [x for x in link_list if x.endswith(fts)]
        if not link_list:
            await ctx.send(embed=error_embed(f"No fancams added for `{idol.title()}`!"))
        if group not in self.recent_dict:
            updater = {group: {}}
            self.recent_dict.update(updater)
        if idol not in self.recent_dict[group]:
            updater = {idol: []}
            self.recent_dict[group].update(updater)
        refine = [x for x in link_list if x not in self.recent_dict[group][idol]]
        if len(refine) <= 1:
            print(f"resetting {group}: {idol} list.")
            self.recent_dict[group][idol] = []
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(refine[0])
            else:
                await ctx.send(refine[0])
        else:
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_dict[group][idol].append(finale)
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(finale)
            else:
                await ctx.send(finale)

# --- Fancam Commands --- #

    @commands.command()
    async def fancam(self, ctx, group, idol, *tags):
        """
        Get a fancam linked for a specified group and idol
        Example: .fancam <group> <idol>
        This can be invoked with tags following <idol>
        Example .fancam <group> <idol> <tag> <tag>
        """
        group = group.lower()
        idol = idol.lower()
        g_id = find_group_id(group)
        if not g_id:
            await ctx.send(embed=error_embed(f'No group added named {group}!'))
            return
        m_id = find_member_id(g_id[0], idol)
        if not m_id:
            await ctx.send(embed=error_embed(f'No idol named {idol} in {group}!'))
            return
        link_list = []
        no_tag = []
        if tags:
            for tag in tags:
                tag = tag.lower()
                # rework sql to take a list of tags at once, rather than multiple
                # https://stackoverflow.com/questions/589284/imploding-a-list-for-use-in-a-python-mysqldb-in-clause
                tagged_links = get_member_links_with_tag(m_id[0], tag)
                if tagged_links:
                    link_list.extend([x[0] for x in tagged_links])
                else:
                    no_tag.append(tag)
        if not link_list:
            links = get_member_links(m_id[0])
            if links:
                link_list.extend([x[0] for x in links])
            else:
                await ctx.send(embed=error_embed(f"No content for `{idol.title()}` in `{group}`!"))
                return
        yt_link = 'https://www.youtu'
        # --- THIS SEEMS TO BE BROKEN --------------------------------------------------------------- #
        link_list = [x[0] for x in link_list if x[0].startswith(yt_link)]
        if not link_list:
            await ctx.send(embed=error_embed(f"No fancams added for `{idol.title()}`!"))
        if group not in self.recent_dict:
            updater = {group: {}}
            self.recent_dict.update(updater)
        if idol not in self.recent_dict[group]:
            updater = {idol: []}
            self.recent_dict[group].update(updater)
        refine = [x for x in link_list if x not in self.recent_dict[group][idol]]
        if len(refine) <= 1:
            print(f"resetting {group}: {idol} list.")
            self.recent_dict[group][idol] = []
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(refine[0])
            else:
                await ctx.send(refine[0])
        else:
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_dict[group][idol].append(finale)
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(finale)
            else:
                await ctx.send(finale)

# --- Gfy/Link Commands --- #

    @commands.command(aliases=[
        'add', 'add_link', 'addgfy', 'add_gfy', 'add_image', 'addimage', 'add_fancam', 'addfancam'])
    async def addlink(self, ctx, group, idol, *args):
        """
        Adds a link to the idols list of gfys with tags following the link
        Example: .addlink <group> <idol> <link_1> <tag> <link_2> <tag> <tag>
        This will add the tags following the link, until the next link!
        If you wish to upload images, you can use discord's upload attachment
        or another external source. Please try to use an image source that
        embeds automatically in discord!
        """
        async with ctx.channel.typing():
            group = group.lower()
            idol = idol.lower()
            links = list(args)
            if ctx.message.attachments:
                x = [x.url for x in ctx.message.attachments]
                links.extend(x)
            if not links:
                await ctx.send(embed=error_embed("No link(s) provided!"))
                return
            g_id = find_group_id(group)
            if not g_id:
                await ctx.send(embed=error_embed(f"{group} does not exist!"))
                return
            m_id = find_member_id(g_id[0], idol)
            if not m_id:
                await ctx.send(embed=error_embed(f"{idol} not in {group}!"))
                return
            author = ctx.author.id
            currentlink = None
            invalid_tags = []
            tags_added = {}
            duplicate_links = 0
            added_links = 0
            valid_tags = [x[0] for x in get_all_tag_names()]
            fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
            for link in links:
                if link.endswith("/"):
                    link = link[:-1]
                if link.startswith("https://gfycat.com/"):
                    split = link.split("/")
                    if "-" in split[-1]:
                        split[-1] = split[-1].split("-")
                        split[-1] = split[-1][0]
                    link = "https://gfycat.com/" + split[-1]
                    currentlink = link
                elif link.startswith("https://www.redgifs.com/"):
                    split = link.split("/")
                    link = "https://www.redgifs.com/watch/" + split[-1]
                    currentlink = link
                elif link.startswith("https://www.gifdeliverynetwork.com/"):
                    split = link.split("/")
                    link = "https://www.gifdeliverynetwork.com/" + split[-1]
                    currentlink = link
                elif link.startswith("https://www.youtu"):
                    currentlink = link
                elif link.endswith(fts):
                    currentlink = link
                elif "twimg" in link:
                    split_link = link.split("/")
                    if "?" in split_link[-1]:
                        splitt = split_link[-1].split("?")
                        if "png" in splitt[-1]:
                            newending = splitt[0] + "?format=png&name=orig"
                        else:
                            newending = splitt[0] + "?format=jpg&name=orig"
                        link = "https://pbs.twimg.com/media/" + newending
                    elif "." in split_link[-1]:
                        splitt = split_link[-1].split(".")
                        if "png" in splitt[-1]:
                            newending = splitt[0] + "?format=png&name=orig"
                        else:
                            newending = splitt[0] + "?format=jpg&name=orig"
                        link = split_link[:-1] + newending
                    currentlink = link
                else:
                    if not currentlink:
                        continue
                    link = link.lower()
                    # tags code is really untested
                    if link not in valid_tags:
                        # check tag is a date format
                        if link.isdecimal() and len(link) == 6:
                            add_tag(link, author)
                            tag_id = find_tag_id(link)
                            add_tag_alias(tag_id, link, author)
                            added_tagged_link = add_link_tags(currentlink, link)
                            if added_tagged_link:
                                if link in tags_added:
                                    tags_added[link] += 1
                                else:
                                    tags_added.update({link: 1})
                        else:
                            invalid_tags.append(link)
                        continue
                    else:
                        link = get_tag_parent_from_alias(link)[0]
                        added = add_link_tags(currentlink, link)
                        if added:
                            if link in tags_added:
                                tags_added[link] += 1
                            else:
                                tags_added.update({link: 1})
                        else:
                            # update to duplicate tags in future
                            invalid_tags.append(link)
                        continue
                if add_link(currentlink, author):
                    l_id = get_link_id(currentlink)
                    added = add_link_to_member(m_id[0], l_id)
                    if added:
                        await self.audit_channel(group, idol, str(link), ctx.author)
                        added_links += 1
                    else:
                        duplicate_links += 1
            # loop end .............................................................. god this function sucks
            embed = discord.Embed(title='Results:',
                                  color=discord.Color.blurple())
            if added_links > 0:
                idol = idol.title()
                embed.add_field(name=f"Added `{added_links}` link(s) to `{group}`'s `{idol}`!",
                                value='\uFEFF',
                                inline=False)
                found = find_user(author)
                if found:
                    add_user_contribution(author, added_links)
                else:
                    add_user(author, 0, added_links)
            if tags_added:
                lets = []
                for key, value in tags_added.items():
                    lets.append(f"{key}: {value}")
                embed.add_field(name=f"Added tagged links to: `{format_list(lets)}`.",
                                value='\uFEFF',
                                inline=False)
            if duplicate_links > 0:
                embed.add_field(name=f"Skipped adding `{duplicate_links}` duplicate link(s).",
                                value='\uFEFF',
                                inline=False)
            if invalid_tags:
                embed.add_field(name=f"Skipped adding duplicate link(s) to tags: `{', '.join(invalid_tags)}` .",
                                value='-',
                                inline=False)
            if not added_links and not tags_added and not duplicate_links and not invalid_tags:
                embed = error_embed("Something went wrong!")
            await ctx.send(embed=embed)

    @commands.command()
    async def gfy(self, ctx, group, idol, *tags):
        """
        Sends a gfy of the specified idol
        Example: .gfy <group> <idol>
        This can be invoked with tags following <idol>
        Example .gfy <group> <idol> <tag> <tag>
        """
        group = group.lower()
        idol = idol.lower()
        g_id = find_group_id(group)
        if not g_id:
            await ctx.send(embed=error_embed(f'No group added named {group}!'))
            return
        m_id = find_member_id(g_id[0], idol)
        if not m_id:
            await ctx.send(embed=error_embed(f'No idol named {idol} in {group}!'))
            return
        link_list = []
        no_tag = []
        if tags:
            for tag in tags:
                tag = tag.lower()
                # rework sql to take a list of tags at once, rather than multiple
                # https://stackoverflow.com/questions/589284/imploding-a-list-for-use-in-a-python-mysqldb-in-clause
                tagged_links = get_member_links_with_tag(m_id[0], tag)
                if tagged_links:
                    link_list.extend([x[0] for x in tagged_links])
                else:
                    no_tag.append(tag)
        if not link_list:
            links = get_member_links(m_id[0])
            if links:
                link_list.extend([x[0] for x in links])
            else:
                await ctx.send(embed=error_embed(f"No content for `{idol.title()}` in `{group}`!"))
                return
        valid_links = (
            "https://gfycat.com/",
            "https://www.redgifs.com/",
            "https://www.gifdeliverynetwork.com/")
        link_list = [x for x in link_list if x.startswith(valid_links)]
        if not link_list:
            await ctx.send(error_embed(f"No links added for `{idol.title()}`!"))
        if group not in self.recent_dict:
            updater = {group: {}}
            self.recent_dict.update(updater)
        if idol not in self.recent_dict[group]:
            updater = {idol: []}
            self.recent_dict[group].update(updater)
        refine = [x for x in link_list if x not in self.recent_dict[group][idol]]
        if len(refine) <= 1:
            print(f"resetting {group}: {idol} list.")
            self.recent_dict[group][idol] = []
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(refine[0])
            else:
                await ctx.send(refine[0])
        else:
            crypto = SystemRandom()
            try:
                rand = crypto.randrange(len(refine) - 1)
            except Exception as e:
                print(e)
                rand = 0
            finale = refine[rand]
            self.recent_dict[group][idol].append(finale)
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(finale)
            else:
                await ctx.send(finale)

# --- Random --- #

    @commands.command(aliases=['r'])
    async def random(self, ctx):
        """Returns a random link, luck of the draw!"""
        async def random_link():
            link_member_group = random_link_from_links()
            link = link_member_group[0]
            idol = link_member_group[1]
            group = link_member_group[2]
            if group not in self.recent_dict:
                updater = {group: {}}
                self.recent_dict.update(updater)
            if idol not in self.recent_dict[group]:
                updater = {idol: []}
                self.recent_dict[group].update(updater)
            if link not in self.recent_dict[group][idol]:
                self.recent_dict[group][idol].append(link)
                await ctx.send(f"Random choice! `{group.title()}`'s `{idol.title()}`\n{link}")
            else:
                relen = len(self.recent_dict[group][idol])
                gflen = member_link_count(group, idol)
                if relen == gflen:
                    print(f"resetting recent dict for {idol}")
                    self.recent_dict[group][idol] = []
                await random_link()

        await random_link()

# --- Tags --- #

    @commands.command()
    async def tags(self, ctx):  # link=None
        """Returns a list of the tags!"""
        tag_list = [x[0] for x in get_all_tag_names()]
        msg = f"`{format_list(tag_list)}`\nSome tags have aliases, to check these try `.tagalias <tag>`"
        embed = discord.Embed(title="Tags:",
                              description=msg,
                              color=discord.Color.blurple())
        await ctx.send(embed=embed)

    @commands.command(aliases=['tagalias', 'talias', 'tag_aliases', 'tagaliases'])
    async def tag_alias(self, ctx, tag):
        """Returns all aliases of a tag!"""
        tag = tag.lower()
        tag_name_and_id = get_tag_parent_from_alias(tag)
        tag_name = tag_name_and_id[0]
        tag_id = tag_name_and_id[-1]
        aliases = [x[0] for x in get_all_alias_of_tag(tag_id)]
        embed = discord.Embed(title=f"Aliases for `{tag_name}`:",
                              description=f"`{format_list(aliases)}`",
                              color=discord.Color.blurple())
        await ctx.send(embed=embed)

    @commands.command()
    async def tag_link(self, ctx, *tags_or_links):
        """
        Adds tag to links previously added.
        Example: .addtag <link> <tag> <tag>
        Example: .addtag <link> <tag> <link> <tag>
        """
        tags_list = tags_or_links
        if not tags_list:
            await ctx.send(error_embed("Not enough arguments provided!"))
            return
        currentlink = None
        valid_links = (
            "https://gfycat.com/",
            "https://www.redgifs.com/",
            "https://www.gifdeliverynetwork.com/",
            "https://pbs.twimg.com/media/",
            "https://youtu",
            "https://www.youtu"
        )
        valid_fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
        valid_tags = [x[0] for x in get_all_tag_names()]
        author = ctx.author.id
        invalid_tags = []
        tags_added = {}
        for tag in tags_list:
            if tag.startswith(valid_links):
                currentlink = tag
            elif tag.endswith(valid_fts):
                currentlink = tag
            else:
                if not currentlink:
                    continue
                tag = tag.lower()
                tag = get_tag_parent_from_alias(tag)[0]
                if tag not in valid_tags:
                    # check tag is a date format
                    if tag.isdecimal() and len(tag) == 6:
                        add_tag(tag, author)
                        tag_id = find_tag_id(tag)
                        add_tag_alias(tag_id, tag, author)
                        added_tagged_link = add_link_tags(currentlink, tag)
                        if added_tagged_link:
                            if tag in tags_added:
                                tags_added[tag] += 1
                            else:
                                tags_added.update({tag: 1})
                    else:
                        invalid_tags.append(tag)
                    continue
                else:
                    added = add_link_tags(currentlink, tag)
                    if added:
                        if tag in tags_added:
                            tags_added[tag] += 1
                        else:
                            tags_added.update({tag: 1})
                    else:
                        # update to duplicate tags in future
                        invalid_tags.append(tag)
                    continue
        embed = discord.Embed(title='Results:',
                              color=discord.Color.blurple())
        if tags_added:
            lets = []
            for key, value in tags_added.items():
                lets.append(f"{key}: {value}")
            embed.add_field(name=f"Added tagged links to: `{format_list(lets)}`.",
                            value='\uFEFF',
                            inline=False)
        if invalid_tags:
            embed.add_field(name=f"Skipped adding duplicate link(s) to tags: `{', '.join(invalid_tags)}` .",
                            value='\uFEFF',
                            inline=False)
        if not invalid_tags and not tags_added:
            embed = error_embed("Something went wrong!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['t'])
    async def tagged(self, ctx, tag):
        """
        Sends a random gfy with the specified tag.
        Example: .tagged <tag>
        """
        tag = tag.lower()
        valid_tags = [x[0] for x in get_all_tag_names()]
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_dict:
                updater = {tag: []}
                self.recent_dict.update(updater)
            taggfy = [x[0] for x in get_links_with_tag(tag)]
            recentag = self.recent_dict[tag]
            refine = [x for x in taggfy if x not in recentag]
            if len(refine) <= 1:
                self.recent_dict[tag] = []
                refine = taggfy
            crypto = SystemRandom()
            try:
                rand = crypto.randrange(len(refine) - 1)
            except Exception as e:
                print(e)
                rand = 0
            finale = refine[rand]
            self.recent_dict[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['ti'])
    async def taggedimage(self, ctx, tag):
        """
        Sends a random image with the specified tag.
        Example: .taggedimage <tag>
        """
        tag = tag.lower()
        valid_fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
        valid_tags = [x[0] for x in get_all_tag_names()]
        twitter = "https://pbs.twimg"
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_dict:
                updater = {tag: []}
                self.recent_dict.update(updater)
            tg = get_links_with_tag(tag)
            recentag = self.recent_dict[tag]
            refine = [x[0] for x in tg if x[0] not in recentag and x[0].endswith(valid_fts) or x[0].startswith(twitter)]
            if len(refine) <= 1:
                self.recent_dict[tag] = []
                refine = tg
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_dict[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['tg'])
    async def taggedgfy(self, ctx, tag):
        """
        Sends a random gfy with the specified tag.
        Example: .taggedgfy <tag>
        """
        valid_links = (
            "https://www.redgifs",
            "https://gfy",
            "https://gifdeliverynetwork"
        )
        tag = tag.lower()
        valid_tags = [x[0] for x in get_all_tag_names()]
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_dict:
                updater = {tag: []}
                self.recent_dict.update(updater)
            taggfy = get_links_with_tag(tag)
            recentag = self.recent_dict[tag]
            refine = [x[0] for x in taggfy if x[0] not in recentag and x[0].startswith(valid_links)]
            if len(refine) <= 1:
                self.recent_dict[tag] = []
                refine = taggfy
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_dict[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['tf'])
    async def taggedfancam(self, ctx, tag):
        """Sends a random fancam with the specified tag."""
        valid_links = (
            "https://youtu",
            "https://www.you"
        )
        tag = tag.lower()
        valid_tags = [x[0] for x in get_all_tag_names()]
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_dict:
                updater = {tag: []}
                self.recent_dict.update(updater)
            taggfy = get_links_with_tag(tag)
            recentag = self.recent_dict[tag]
            refine = [x[0] for x in taggfy if x[0] not in recentag and x[0].startswith(valid_links)]
            if len(refine) <= 1:
                self.recent_dict[tag] = []
                refine = taggfy
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_dict[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

# --- Timer Commands --- #

    @commands.command(aliases=['nohands'])
    async def timer(self, ctx, *args):
        """
        Sends a gfy in the channel every user defined interval in seconds
        (minimum is 10 seconds) for a duration (maximum of 30 minutes) of time.
        When calling state the duration in minutes, and the interval in seconds
        Example: .timer <duration(min)> <interval(sec)> <group> <idol>
        Example: .timer 10 10 RedVelvet Joy
        If the interval is omitted, it will default to 10 seconds.
        Example: .timer 10 RedVelvet Joy
        This command can be invoked with tags after <idol> add, <tag>.
        """
        await self.disclient.wait_until_ready()
        no_interval = False
        try:
            int(args[1])
        except ValueError:
            no_interval = True

        duration = int(args[0])

        if no_interval:
            group = args[1].lower()
            idol = args[2].lower()
            tags = args[3:]
            interval = 10
        else:
            interval = int(args[1])
            group = args[2].lower()
            idol = args[3].lower()
            tags = args[4:]

        gid = find_group_id(group)
        if not gid:
            await ctx.send(error_embed(f"Nothing for {group}"))
            return
        mid = find_member_id(gid[0], idol)
        if not mid:
            await ctx.send(error_embed(f"Nothing for {idol} in {group}"))
        else:
            if interval < 10:
                interval = 10
            if duration > 30:
                duration = 30
            loops = int((duration * 60) // interval)
            author = str(ctx.author)
            checklist = []
            for keys in self.loops:
                if keys.startswith(author):
                    checklist.append(keys)
            if len(checklist) >= 1:
                checklist.sort()
                author = checklist[-1] + "_"
            t = len(str(author)) - len(str(ctx.author)) + 1
            await ctx.send(f"This is timer number `{t}` for `{ctx.author}`.")
            loop_and_author = {author: loops}
            self.loops.update(loop_and_author)
            try:
                while self.loops[author] > 0:
                    await self.gfy(ctx, group, idol, *tags)
                    self.loops[author] -= 1
                    if self.loops[author] <= 0:
                        await ctx.send("Timer finished.")
                        self.loops.pop(author)
                    await asyncio.sleep(interval)
            except KeyError:
                pass
                return

    @commands.command(aliases=['stop'])
    async def stop_timer(self, ctx, timer_number=None):
        """
        Stops the timer function by user, if you have multiple timers running, specify the timer number.
        You can stop all timers with: .stop all
        """
        if timer_number:
            pass
        else:
            timer_number = 1
        author = str(ctx.author)
        checklist = []
        for keys in self.loops:
            if keys.startswith(author):
                checklist.append(keys)

        if str(timer_number) == 'all':
            i = 0
            for element in checklist:
                self.loops[element] = 0
                self.loops.pop(element)
                i += 1
            await ctx.send(f"Stopped all {i} timers for `{author}`")
        elif len(checklist) == 1:
            self.loops[checklist[0]] = 0
            self.loops.pop(checklist[0])
            await ctx.send(f"Stopped timer for `{author}`.")
        elif len(checklist) > 1:
            to_stop = len(author) + timer_number - 1
            checklist.sort()
            for element in checklist:
                if len(element) == to_stop:
                    author = element
            self.loops[author] = 0
            await ctx.send(
                    f"Stopped timer `{timer_number}` for `{ctx.author}`.")
            self.loops.pop(author)
            print(f"deleted {author} from loops")
        else:
            await ctx.send(f"No timers running for `{ctx.author}`.")

# --- Info Commands --- #

    @commands.command()
    async def info(self, ctx, group=None, idol=None):
        """
        returns info about the groups added to the bot,
        or the group specified, or the idol specified.
        Example: .info
        Example: .info <group>
        Example: .info <group> <idol>
        """
        async with ctx.channel.typing():
            if group is None:
                groups = get_groups()
                groups = [x[0] for x in groups]
                group_msg = f"`{format_list(groups)}`"
                s = "Type `.info <group>` for more information on that group!"
                embed = discord.Embed(title='Groups:',
                                      description=group_msg + '\n\n' + s,
                                      color=discord.Color.blurple())
                await ctx.send(embed=embed)
            elif group is not None and idol is None:
                group = group.lower()
                name_and_g_id = find_group_id_and_name(group)
                if name_and_g_id:
                    g_id = name_and_g_id[0]
                    g_name = name_and_g_id[-1]
                    message = []
                    aliases = [x[0] for x in get_group_aliases(g_id)]
                    members = get_members_of_group_and_link_count(g_id)
                    for member in members:
                        name = member[0]
                        number_of_links = member[1]
                        spacing = ' ' * (35 - (len(name) + len(str(number_of_links))))
                        memb = f"{name.title()}{spacing}{number_of_links}"
                        message.append(memb)
                    nl = "Link Count"
                    mes = f"""`Name {' ' * (30 - len(nl))}{nl}`\n`{format_list_newline(message)}`
                           \n{g_name} has aliases: `{'`, `'.join(aliases)}`
                           \nTry `.info {group} <idol>` for more information!"""
                    embed = discord.Embed(title=f"{g_name} Members",
                                          description=mes,
                                          color=discord.Color.blurple())
                    await ctx.send(embed=embed)
                elif name_and_g_id is None:
                    await ctx.send(embed=error_embed(f'No group called {group}!\nTry `.info` to see a list of groups!'))
            elif idol is not None and group is not None:
                idol = idol.lower()
                group = group.lower()
                g_id_and_name = find_group_id_and_name(group)
                if not g_id_and_name:
                    await ctx.send(embed=error_embed(f"No group called {group}!"))
                    return
                g_id = g_id_and_name[0]
                g_name = g_id_and_name[-1]
                m_id_and_name = find_member_id_and_name(g_id, idol)
                if not m_id_and_name:
                    await ctx.send(embed=error_embed(f"No idol called {idol} in {group}!"))
                    return
                m_id = m_id_and_name[0]
                m_name = m_id_and_name[-1]
                link_count = count_links_of_member(m_id)
                member_aliases = [x[0] for x in find_member_aliases(m_id)]
                is_tagged = []
                tags_and_count = get_all_tags_on_member_and_count(m_id)
                for tags in tags_and_count:
                    is_tagged.append(f"{tags[0]}: {tags[1]}")
                a = f'{g_name} {m_name.title()} Information'
                d = hide_links([x[0] for x in last_three_links(m_id)])
                if is_tagged:
                    c = format_list(is_tagged)
                    s = (f'`{m_name.title()}` has a total of `{link_count}` link(s)!\n'
                         f'**Alias(es):** `{"`, `".join(member_aliases)}`\n'
                         f'**Tags:** `{c}`')
                else:
                    s = (f'`{m_name.title()}` has `{link_count}` link(s)!\n'
                         f'**Alias(es):** {format_list(member_aliases)}')
                if d:
                    s = s + f'\nThe last 3 links added:\n<{d}>'

                embed = discord.Embed(title=f'**{a}**',
                                      description=s,
                                      color=discord.Color.blurple())
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=error_embed(f"No group named `{group}`!"))

    @commands.command(aliases=['linkcount', 'total_links'])
    async def totallinks(self, ctx):
        results = count_links()
        group_count = results[1]
        member_count = results[2]
        link_count = results[0]
        des = (f"There are currently `{link_count}` links of "
               f"`{member_count}` idols belonging to "
               f"`{group_count}` groups!")
        embed = discord.Embed(title='Total Links',
                              description=des,
                              color=discord.Color.blurple())
        await ctx.send(embed=embed)

    # @commands.command(aliases=['list'])
    # async def listlinks(self, ctx, group, idol=None):
    #     """
    #     Returns a list of all links that belong to a specified group, or idol
    #     This command can be envoked with .listlinks OR .list
    #     Examples:
    #     .list <group>
    #     .list <group> <idol>
    #     .list redvelvet
    #     .list redvelvet joy
    #     """
    #     async with ctx.channel.typing():
    #         if not idol:
    #             group = group.lower()
    #             if group in dicto:
    #                 o = f'{group} \n'
    #                 msg = [o]
    #                 for m in dicto[group]:
    #                     s = (f"{m}: \n"
    #                          f"<{newline(dicto[group][m])}>")
    #                     print(f"s string: {s}")
    #                     msg.append(s)
    #                 sen = '\n'.join(msg)
    #                 if len(sen) > 1500:
    #                     await ctx.message.add_reaction(emoji='✉')
    #                     send = []
    #                     n = 1500
    #                     while sen:
    #                         if len(sen) > n:
    #                             send.append(sen[:n])
    #                             sen = sen[n:]
    #                         else:
    #                             send.append(sen)
    #                             break
    #                     for elem in send:
    #                         await ctx.message.author.send(elem)
    #                 else:
    #                     await ctx.message.add_reaction(emoji='✉')
    #                     await ctx.message.author.send(sen)
    #             else:
    #                 des = f"No group named {group}!"
    #                 er = discord.Embed(title='Error!',
    #                                    description=des,
    #                                    color=discord.Color.red())
    #                 await ctx.message.add_reaction(emoji='✉')
    #                 await ctx.message.author.send(embed=er)
    #         elif idol:
    #             group = group.lower()
    #             idol = idol.lower()
    #             if group in dicto:
    #                 if idol in dicto[group]:
    #                     s = (f"All links for: `{idol}`: \n"
    #                          f"<{newline(dicto[group][idol])}>")
    #                     if len(s) > 1500:
    #                         await ctx.message.add_reaction(emoji='✉')
    #                         send = []
    #                         n = 1500
    #                         # need to pick to cut so that links are not sent like;
    #                         # <https://gfycat.com/blushing
    #                         # shadyhoiho-jennie>
    #                         # due to the cutting at 1500 intervals
    #                         while s:
    #                             if len(s) > n:
    #                                 send.append(s[:n])
    #                                 s = s[n:]
    #                             else:
    #                                 send.append(s)
    #                                 break
    #                         for elem in send:
    #                             await ctx.message.author.send(elem)
    #                     else:
    #                         await ctx.message.add_reaction(emoji='✉')
    #                         await ctx.message.author.send(s)
    #                 else:
    #                     des = f"No `{idol}` in `{group}`!"
    #                     er = discord.Embed(title='Error!',
    #                                        description=des,
    #                                        color=discord.Color.red())
    #                     await ctx.message.add_reaction(emoji='✉')
    #                     await ctx.message.author.send(embed=er)
    #             else:
    #                 des = f"No group named `{group}`!"
    #                 er = discord.Embed(title='Error!',
    #                                    description=des,
    #                                    color=discord.Color.red())
    #                 await ctx.message.add_reaction(emoji='✉')
    #                 await ctx.message.author.send(embed=er)
    #         else:
    #             des = "Invalid arguments! Try again or try `.help list`"
    #             er = discord.Embed(title='Error!',
    #                                description=des,
    #                                color=discord.Color.red())
    #             await ctx.message.add_reaction(emoji='✉')
    #             await ctx.message.author.send(embed=er)

# --- Auditing --- #

    async def audit_channel(self, group, idol, link, author):
        """
        To keep gfycat links safe and within rules of what can be added
        main channel is in the official discord, other auditing channels can
        be made by mods, author names will be omitted in those.
        """
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        main_audcha = self.disclient.get_channel(apis_dict["auditing_channel"])
        s = f'Time Added: `{dt}`\nGroup: `{group}`\nIdol: `{idol}`\nLink: {link}'
        embed = discord.Embed(title=s,
                              color=discord.Color.blurple())
        embed.set_footer(text=f"Added by {author}",
                         icon_url=author.avatar_url)
        await main_audcha.send(embed=embed)
        await main_audcha.send(link)
        aud_chas = get_auditing_channels()
        if aud_chas:
            list_of_chas = [x[0] for x in aud_chas]
            for chan in list_of_chas:
                channel = self.disclient.get_channel(int(chan))
                fstr = f'Added: `{group}`, `{idol}`: {link}'
                try:
                    await channel.send(fstr)
                except AttributeError:
                    print("channel deleted")
                    remove_auditing_channel(chan)


# --- End of Class --- #


def format_list(array):
    formatted = '`, `'.join(array)
    return formatted


def format_list_newline(array):
    formatted = '`\n`'.join(array)
    return formatted


def hide_links(array):
    hidden = '> <'.join(array)
    return hidden


def newline(array):
    newliner = '>\n<'.join(array)
    return newliner


def setup(disclient):
    disclient.add_cog(Fun(disclient))
