import discord
from discord.ext import commands
from random import SystemRandom
import asyncio
from datetime import datetime
from embeds import error_embed, warning_embed, success_embed, restricted_embed

# import lots of shit from datafile.
from data import find_group_id, get_member_links_with_tag, get_member_links, find_member_id, get_all_alias_of_tag, \
    find_member_aliases, find_group_id_and_name, get_group_aliases, find_member_id_and_name, \
    get_tag_parent_from_alias, get_all_tag_names, add_tag, find_tag_id, add_tag_alias, add_link_tags, \
    add_link, get_link_id, add_link_to_member, find_user, add_user_contribution, add_user, \
    random_link_from_links, member_link_count, get_links_with_tag, get_groups, \
    get_members_of_group_and_link_count, count_links_of_member, get_all_tags_on_member_and_count, \
    last_three_links, count_links, apis_dict, get_auditing_channels, remove_auditing_channel, find_restricted_user_db, \
    find_perma_db, cache_dict, random_links_without_tags, get_guild_max_duration, gfy_v2_test, gfy_v2_test_tags, \
    get_all_tag_alias_names


# custom decorators


def is_restricted():
    async def is_restricted_predicate(ctx):
        if ctx.guild is None:
            return True
        x = find_restricted_user_db(ctx.guild.id, ctx.author.id)
        return False if x else True
    return commands.check(is_restricted_predicate)


def is_perma():
    async def perma(ctx):
        x = find_perma_db(ctx.author.id)
        return False if x else True
    return commands.check(perma)


def links_with_tag(idol_id, *tags):
    link_list = []
    no_tag = []
    for tag in tags:
        tag = tag.lower()
        # rework sql to take a list of tags at once, rather than multiple
        # https://stackoverflow.com/questions/589284/imploding-a-list-for-use-in-a-python-mysqldb-in-clause
        tagged_links = get_member_links_with_tag(idol_id[0], tag)
        if tagged_links:
            link_list.extend([x[0] for x in tagged_links])
        else:
            no_tag.append(tag)
    return link_list, no_tag


def send_gfy_error_formatting(group, idol):
    g_id = find_group_id(group)
    if not g_id:
        return f'No group added named {group}!'
    m_id = find_member_id(g_id[0], idol)
    if not m_id:
        return f'No idol named {idol} in {group}!'
    else:
        return f"No content for `{idol}` in `{group}`!"


def rows_of_links(group, idol):
    group = group.lower()
    idol = idol.lower()
    rows = gfy_v2_test(group, idol)
    return rows


def rows_of_links_with_tags(group, idol, *tags):
    group = group.lower()
    idol = idol.lower()
    rows = []
    for tag in tags:
        rows.extend(gfy_v2_test_tags(group, idol, tag[0]))
    return rows


def format_timer_args(args):
    no_interval = False
    no_duration = False
    try:
        interval = int(args[1])
    except ValueError:
        no_interval = True
        interval = 10
    try:
        duration = int(args[0])
    except ValueError:
        duration = 1
        no_duration = True
    if no_duration and no_interval:
        group = args[0].lower()
        idol = args[1].lower()
        tags = args[2:]
    elif no_interval:
        group = args[1].lower()
        idol = args[2].lower()
        tags = args[3:]
    else:
        interval = int(args[1])
        group = args[2].lower()
        idol = args[3].lower()
        tags = args[4:]
    if interval < 10:
        interval = 10
    if duration > 30:
        duration = 30
    elif duration <= 0:
        duration = 1
    return duration, interval, group, idol, tags


class Fun(commands.Cog):
    """All of the commands listed here are for gfys, images, or fancams.
    All groups with multiple word names are written as one word.
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        self.loops = cache_dict["gfys"]["loops"]  # dict for timers
        self.recent_posts = cache_dict["gfys"]["recent_posts"]
        self.VALID_LINK_GFY = ("https://gfycat.com",
                               "https://www.redgifs.com",
                               "https://www.gifdeliverynetwork.com")
        # self.disclient.loop.create_task(self.write_recent())

    # @commands.Cog.listener()
    # async def write_recent(self):
    #     await self.disclient.wait_until_ready()
    #     while not self.disclient.is_closed():
    #         with open(direc_dict["recents"], 'w') as rece:
    #             json.dump(recent_dict, rece, indent=4)
    #         await asyncio.sleep(5)

    @commands.command()
    @is_restricted()
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
        if group not in self.recent_posts:
            updater = {group: {}}
            self.recent_posts.update(updater)
        if idol not in self.recent_posts[group]:
            updater = {idol: []}
            self.recent_posts[group].update(updater)
        refine = [x for x in link_list if x not in self.recent_posts[group][idol]]
        if len(refine) <= 1:
            print(f"resetting {group}: {idol} list.")
            self.recent_posts[group][idol] = []
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
            self.recent_posts[group][idol].append(finale)
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(finale)
            else:
                await ctx.send(finale)

# --- Fancam Commands --- #

    @commands.command()
    @is_restricted()
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
        # THIS SEEMS TO BE BROKEN --------------------------------------------------------------- #
        link_list = [x[0] for x in link_list if x[0].startswith(yt_link)]
        if not link_list:
            await ctx.send(embed=error_embed(f"No fancams added for `{idol.title()}`!"))
        if group not in self.recent_posts:
            updater = {group: {}}
            self.recent_posts.update(updater)
        if idol not in self.recent_posts[group]:
            updater = {idol: []}
            self.recent_posts[group].update(updater)
        refine = [x for x in link_list if x not in self.recent_posts[group][idol]]
        if len(refine) <= 1:
            print(f"resetting {group}: {idol} list.")
            self.recent_posts[group][idol] = []
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
            self.recent_posts[group][idol].append(finale)
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await ctx.send(embed=warning_embed(msg))
                await ctx.send(finale)
            else:
                await ctx.send(finale)

# --- Gfy/Link Commands --- #

    @commands.command(aliases=[
        'add', 'add_link', 'addgfy', 'add_gfy', 'add_image', 'addimage', 'add_fancam', 'addfancam'])
    @is_restricted()
    @is_perma()
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
            last_added = None
            invalid_tags = {}
            duplicate_tags = {}
            tags_added = {}
            duplicate_links = 0
            added_links = 0
            valid_tags = [x[0] for x in get_all_tag_alias_names()]
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
                    last_added = None
                elif link.startswith("https://www.redgifs.com/"):
                    split = link.split("/")
                    link = "https://www.redgifs.com/watch/" + split[-1]
                    currentlink = link
                    last_added = None
                elif link.startswith("https://www.gifdeliverynetwork.com/"):
                    split = link.split("/")
                    link = "https://www.gifdeliverynetwork.com/" + split[-1]
                    currentlink = link
                    last_added = None
                elif link.startswith("https://www.youtu"):
                    currentlink = link
                    last_added = None
                elif link.endswith(fts):
                    currentlink = link
                    last_added = None
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
                        link = "https://pbs.twimg.com/media/" + newending
                    currentlink = link
                    last_added = None
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
                            if link not in invalid_tags:
                                invalid_tags.update({link: [currentlink]})
                            else:
                                invalid_tags[link].append(currentlink)
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
                            if link not in duplicate_tags:
                                duplicate_tags.update({link: [currentlink]})
                            else:
                                duplicate_tags[link].append(currentlink)
                            continue
                if add_link(currentlink, author):
                    l_id = get_link_id(currentlink)
                    added = add_link_to_member(m_id[0], l_id)
                    if added:
                        await self.audit_channel(group, idol, str(link), ctx.author)
                        added_links += 1
                        last_added = currentlink
                    else:
                        if currentlink == last_added:
                            continue
                        else:
                            duplicate_links += 1
            # loop end .............................................................. this function loool
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
                    # TODO add messaging to users adding a lot, to invite them to main discord
                    # check add check to database as to whether they have been messaged
                    # also check that they are not currently in the discord
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
            if duplicate_tags:
                embed.add_field(name=f"Skipped adding duplicate link(s) to tag(s): `{', '.join(duplicate_tags)}` .",
                                value='\uFEFF',
                                inline=False)
            if invalid_tags:
                embed.add_field(name=f"The following tags are invalid: `{', '.join(invalid_tags)}` .",
                                value='\uFEFF',
                                inline=False)
            if not added_links and not tags_added and not duplicate_links and not invalid_tags:
                embed = error_embed("Something went wrong!")
            await ctx.send(embed=embed)

    def add_to_recent_posts(self, group, idol):
        if group not in self.recent_posts:
            updater = {group: {}}
            self.recent_posts.update(updater)
        if idol not in self.recent_posts[group]:
            updater = {idol: []}
            self.recent_posts[group].update(updater)

    def return_gfys(self, group, idol, tags):
        if tags:
            print("there are tags")
            rows = rows_of_links_with_tags(group, idol, tags)
            if not rows:
                print("nothing for that tag")
                rows = rows_of_links(group, idol)
        else:
            print("no tags")
            rows = rows_of_links(group, idol)
        # row = (groupid, memberid, gromanname, mromanname, link)
        if len(rows) >= 1:
            return self.return_link_from_rows(rows)
        else:
            # handle error here
            error = send_gfy_error_formatting(group, idol)
            if error:
                return error_embed(error)

    def return_link_from_rows(self, rows):
        """x: row: (gid, mid, gname, mname, link)"""
        group = rows[0][2]
        idol = rows[0][3]
        self.add_to_recent_posts(group, idol)
        links = [
            x[-1] for x in rows if x[-1] not in self.recent_posts[x[2]][x[3]] and x[-1].startswith(self.VALID_LINK_GFY)]
        print(links)
        if not links:
            print("not a single link left, resetting recent post")
            links = [x[-1] for x in rows if x[-1].startswith(self.VALID_LINK_GFY)]
            self.recent_posts[group][idol] = []
        crypto = SystemRandom()
        try:
            rand = crypto.randrange(len(links) - 1)
        except ValueError:
            rand = 0
        finale = links[rand]
        if len(links) <= 1:
            self.recent_posts[group][idol] = []
        else:
            self.recent_posts[group][idol].append(finale)
        return finale

    @commands.command(name='gfy', aliases=['gif', 'gyf', 'jif'])
    @is_restricted()
    async def _gfyv2(self, ctx, group, idol, *tags):
        """Returns a gfy from the requested group and idol!
        Examples: `.gfy <group> <idol>`, `.gfy RV Joy`
        You can also add tags after the idol arguement"""
        group = group.lower()
        idol = idol.lower()
        tags = tags
        result = self.return_gfys(group, idol, tags)
        if isinstance(result, discord.Embed):
            # this is an error
            await ctx.send(embed=result)
        else:
            await ctx.send(result)

# --- Random --- #

    @commands.command(aliases=['r'])
    @is_restricted()
    async def random(self, ctx):
        """Returns a random link, luck of the draw!"""

        async def random_link():
            link_member_group = random_link_from_links()
            link = link_member_group[0]
            idol = link_member_group[1]
            group = link_member_group[2]
            self.add_to_recent_posts(group, idol)
            if link not in self.recent_posts[group][idol]:
                self.recent_posts[group][idol].append(link)
                await ctx.send(f"Random choice! `{group.title()}`'s `{idol.title()}`\n{link}")
            else:
                relen = len(self.recent_posts[group][idol])
                gflen = member_link_count(group, idol)
                if relen == gflen:
                    print(f"resetting recent dict for {idol}")
                    self.recent_posts[group][idol] = []
                await random_link()

        await random_link()

# --- Tags --- #

    @commands.command()
    @is_restricted()
    async def tags(self, ctx):  # link=None
        """Returns a list of the tags!"""
        tag_list = [x[0] for x in get_all_tag_names() if len(x[0]) != 6 and not x[0].isdecimal()]
        msg = f"`{format_list(tag_list)}`\nSome tags have aliases, to check these try `.tagalias <tag>`\n" \
              f"Dates are also available, check out `.dates` to see them!"
        embed = discord.Embed(title="Tags:",
                              description=msg,
                              color=discord.Color.blurple())
        await ctx.send(embed=embed)

    @commands.command()
    @is_restricted()
    async def dates(self, ctx):
        date_list = [x[0] for x in get_all_tag_names() if len(x[0]) == 6 and x[0].isdecimal()]
        msg = f"`{format_list(date_list)}`"
        embed = discord.Embed(title="Dates:",
                              description=msg,
                              color=discord.Color.blurple())
        await ctx.send(embed=embed)

    @commands.command(aliases=['tagalias', 'talias', 'tag_aliases', 'tagaliases'])
    @is_restricted()
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

    @commands.command(aliases=['addtag', 'taglink', 'add_tag'])
    @is_restricted()
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
        valid_tags = [x[0] for x in get_all_tag_alias_names()]
        author = ctx.author.id
        invalid_tags = []
        duplicate_tags = []
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
                        duplicate_tags.append(tag)
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
        if duplicate_tags:
            embed.add_field(name=f"Skipped adding duplicate link(s) to tags: `{', '.join(duplicate_tags)}` .",
                            value='\uFEFF',
                            inline=False)
        if invalid_tags:
            embed.add_field(name=f"The following tags are invalid: `{', '.join(invalid_tags)}` .",
                            value='\uFEFF',
                            inline=False)
        if not invalid_tags and not tags_added and not duplicate_tags:
            embed = error_embed("Something went wrong!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['t'])
    @is_restricted()
    async def tagged(self, ctx, tag):
        """
        Sends a random gfy with the specified tag.
        Example: .tagged <tag>
        """
        tag = tag.lower()
        valid_tags = [x[0] for x in get_all_tag_alias_names()]
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_posts:
                updater = {tag: []}
                self.recent_posts.update(updater)
            taggfy = [x[0] for x in get_links_with_tag(tag)]
            recentag = self.recent_posts[tag]
            refine = [x for x in taggfy if x not in recentag]
            if len(refine) <= 1:
                self.recent_posts[tag] = []
                refine = taggfy
            crypto = SystemRandom()
            try:
                rand = crypto.randrange(len(refine) - 1)
            except Exception as e:
                print(e)
                rand = 0
            finale = refine[rand]
            self.recent_posts[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['ti'])
    async def taggedimage(self, ctx, tag):
        """
        Sends a random image with the specified tag.
        Example: .taggedimage <tag>
        """
        if ctx.guild:
            if find_restricted_user_db(ctx.guild.id, ctx.author.id):
                await ctx.author.send(embed=restricted_embed(ctx.guild))
                return
        tag = tag.lower()
        valid_fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
        valid_tags = [x[0] for x in get_all_tag_alias_names()]
        twitter = "https://pbs.twimg"
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_posts:
                updater = {tag: []}
                self.recent_posts.update(updater)
            tg = get_links_with_tag(tag)
            recentag = self.recent_posts[tag]
            refine = [x[0] for x in tg if x[0] not in recentag and x[0].endswith(valid_fts) or x[0].startswith(twitter)]
            if len(refine) <= 1:
                self.recent_posts[tag] = []
                refine = tg
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_posts[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['tg'])
    @is_restricted()
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
        valid_tags = [x[0] for x in get_all_tag_alias_names()]
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_posts:
                updater = {tag: []}
                self.recent_posts.update(updater)
            taggfy = get_links_with_tag(tag)
            recentag = self.recent_posts[tag]
            refine = [x[0] for x in taggfy if x[0] not in recentag and x[0].startswith(valid_links)]
            if len(refine) <= 1:
                self.recent_posts[tag] = []
                refine = taggfy
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_posts[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['tf'])
    @is_restricted()
    async def taggedfancam(self, ctx, tag):
        """Sends a random fancam with the specified tag."""
        valid_links = (
            "https://youtu",
            "https://www.you"
        )
        tag = tag.lower()
        valid_tags = [x[0] for x in get_all_tag_alias_names()]
        if tag in valid_tags:
            tag = get_tag_parent_from_alias(tag)[0]
            if tag not in self.recent_posts:
                updater = {tag: []}
                self.recent_posts.update(updater)
            taggfy = get_links_with_tag(tag)
            recentag = self.recent_posts[tag]
            refine = [x[0] for x in taggfy if x[0] not in recentag and x[0].startswith(valid_links)]
            if len(refine) <= 1:
                self.recent_posts[tag] = []
                refine = taggfy
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_posts[tag].append(finale)
            await ctx.send(f"Tagged `{tag}`, {finale}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['tagupdater'])
    @is_restricted()
    async def tag_updater(self, ctx, *args):
        """Returns a number of random links that do not have tags, for the purpose of tagging them.
        Optional arguments of group, or idol
        Examples:
        .tag_updater 2
        .tag_updater 4 RedVelvet
        .tag_updater 4 RedVelvet Joy
        .tag_updater <number_of_links, default=4> <group_name, optional> <idol_name, optional>"""
        try:
            int(args[0])
            number_of_links = int(args[0])
            group = args[1]
            if len(args) >= 3:
                idol = args[2]
            else:
                idol = None
        except ValueError:
            number_of_links = 4
            group = args[0]
            if len(args) >= 2:
                idol = args[1]
            else:
                idol = None
        if number_of_links > 4:
            if ctx.guild:
                await ctx.author.send(
                    embed=warning_embed('Please refrain from using tag_updater for more than 4 links in a server!'))
                number_of_links = 4
        elif number_of_links > 30:
            number_of_links = 30
        links = random_links_without_tags(number_of_links, group, idol)
        print(links)
        # link is a tuple of 3 parts, 0: link, 1: member name, 2: group name
        send = f"The following links have no tags assigned to them!\n"
        if not links:
            await ctx.send(embed=warning_embed('No links without tags!'))
            return
        if number_of_links <= 4:
            for link in links:
                # can send all links in one message
                send = send + f"{link[2]}'s {link[1]}: {link[0]}\n"
            await ctx.send(send)
        else:
            i = 0
            for link in links:
                send = send + f"{link[2]}'s {link[1]}: {link[0]}\n"
                i += 1
                if i == 4:
                    await ctx.send(send)
                    i = 0
                    send = ''
            if send:
                await ctx.send(send)

# --- Timer Commands --- #

    @commands.command(name='timer', aliases=['nohands'])
    @is_restricted()
    async def _timer(self, ctx, *args):
        duration, interval, group, idol, tags = format_timer_args(args)
        msg = ''
        if ctx.guild:
            max_duration = get_guild_max_duration(ctx.guild.id)
            if max_duration:
                if duration > max_duration[0]:
                    duration = max_duration[0]
                    msg = msg + f'\nDuration reduced to server max duration of `{max_duration[0]}`.'
        if tags:
            links = rows_of_links_with_tags(group, idol, tags)
        else:
            links = rows_of_links(group, idol)
        loops = (abs(duration) * 60) // abs(interval)
        if len(links) < loops:
            loops = len(links)
        author = str(ctx.author.id)
        channel = str(ctx.channel.id)
        if channel not in self.loops:
            self.loops.update({channel: {}})
        if author not in self.loops[channel]:
            self.loops[channel].update({author: {'1': loops}})
            index = '1'
        else:
            try:
                index = int(max(self.loops[channel][author].keys())) + 1
            except ValueError:
                index = '1'
            index = str(index)
            self.loops[channel][author].update({index: loops})
        msg = f"{group}'s {idol} for {duration} minute(s)!" + msg
        await ctx.send(embed=discord.Embed(title='Starting Timer!',
                                           description=msg,
                                           color=discord.Color.blurple()))
        try:
            while self.loops[channel][author][index] > 0:
                await ctx.send(self.return_link_from_rows(links))
                self.loops[channel][author][index] -= 1
                if self.loops[channel][author][index] == 0:
                    await ctx.send(embed=discord.Embed(title='Timer Finished!',
                                                       description='',
                                                       color=discord.Color.blurple()))
                    break
                await asyncio.sleep(interval)
        except KeyError:
            pass
        if self.loops[channel][author][index] == 0:
            self.loops[channel][author].pop(index)
        if not self.loops[channel][author]:
            self.loops[channel].pop(author)
        if not self.loops[channel]:
            self.loops.pop(channel)

    @commands.command(aliases=['stop', 'cancel', 'end'])
    @is_restricted()
    async def stop_timer(self, ctx, timer_number=None):
        """
        Stops the timer function by user, if you have multiple timers running, specify the timer number.
        You can stop all timers with: .stop all
        """

        author = str(ctx.author.id)
        channel = str(ctx.channel.id)
        if channel not in self.loops:
            await ctx.send(embed=error_embed('No timer running in this channel.'))
            return
        if author not in self.loops[channel]:
            await ctx.send(embed=error_embed('No timer running for {ctx.author} in this channel.'))
            return
        if not timer_number:
            timer_number = min(self.loops[channel][author].keys())
        if timer_number == 'all':
            for element in self.loops[channel][author].keys():
                self.loops[channel][author].pop(element)
            await ctx.send(embed=discord.Embed(title='Stopped Timer',
                                               description=f"Stopped all timers for `{ctx.author}`",
                                               color=discord.Color.blurple()))
        else:
            self.loops[channel][author].pop(timer_number)
            await ctx.send(embed=discord.Embed(title='Stopped Timer',
                                               description=f"Stopped timer {timer_number} for {ctx.author}",
                                               color=discord.Color.blurple()))

    @commands.command(name='force_stop', aliases=['stoptimer', 'stopusertimer', 'forcestop'])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @is_restricted()
    async def _destroy_timers(self, ctx, member: discord.Member):
        """Force all timers started by a user to end.
        Usage (invoke this command in the same channel that the timer is running):
        .force_stop @<user>
        .force_stop <User ID>"""
        channel = str(ctx.channel.id)
        member_id = str(member.id)
        destroyed = 0
        if channel in self.loops:
            if member_id in self.loops[channel]:
                destroyed += len(self.loops[channel][member_id])
                del self.loops[channel][member_id]
            else:
                await ctx.send(embed=error_embed(f'No timers running for `{member}`!'))
        else:
            await ctx.send(embed=error_embed('No timers running in this channel!'))
        if destroyed > 0:
            await ctx.send(embed=success_embed(f'Destroyed {destroyed} timers running for `{member}`'))

# --- Info Commands --- #

    @commands.command()
    @is_restricted()
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
    @is_restricted()
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
        s = f'Time Added: `{dt}`\nUser ID: `{author.id}`\nGroup: `{group}`\nIdol: `{idol}`\nLink: {link}'
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
