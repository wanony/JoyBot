from datetime import datetime, timedelta

import nextcord as discord
import nextcord.errors
from nextcord import SlashOption
from nextcord.ext import commands
from random import SystemRandom
import asyncio
from embeds import error_embed, warning_embed, success_embed

# import lots from the datafile.
from data import find_group_id, get_member_links_with_tag, get_member_links, find_member_id, get_all_alias_of_tag, \
    find_member_aliases, find_group_id_and_name, get_group_aliases, find_member_id_and_name, \
    get_tag_parent_from_alias, get_all_tag_names, add_tag, find_tag_id, add_tag_alias, add_link_tags, \
    add_link, get_link_id, add_link_to_member, find_user, add_user_contribution, add_user, \
    random_link_from_links, member_link_count, get_links_with_tag, get_groups, \
    get_members_of_group_and_link_count,  get_all_tags_on_member_and_count, \
    last_three_links, count_links, apis_dict, get_auditing_channels, remove_auditing_channel, find_restricted_user_db, \
    find_perma_db, cache_dict, get_guild_max_duration, gfy_v2_test, gfy_v2_test_tags, \
    get_all_tag_alias_names, pick_groups, pick_group_members, pick_tags, pick_tags_on_idol, gfy_v2_test_tags_group_only


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


def send_gfy_error_formatting(group, idol=None):
    if idol:
        g_id = find_group_id(group)
        if not g_id:
            return f'No group added named {group}!'
        m_id = find_member_id(g_id[0], idol)
        if not m_id:
            return f'No idol named {idol} in {group}!'
        else:
            return f"No content for `{idol}` in `{group}`!"
    else:
        g_id = find_group_id(group)
        if not g_id:
            return f'No group added named {group}!'


def rows_of_links(group, idol):
    group = group.lower()
    idol = idol.lower()
    rows = gfy_v2_test(group, idol)
    return rows


def rows_of_group_links(group):
    group = group.lower()
    rows = gfy_v2_test(group)
    return rows


def rows_of_links_with_tags(group, tags, idol=None):
    if idol:
        group = group.lower()
        idol = idol.lower()
        rows = []
        for tag in tags:
            rows.extend(gfy_v2_test_tags(group, idol, tag.lower()))
    else:
        group = group.lower()
        rows = []
        for tag in tags:
            # TODO TEST THIS
            rows.extend(gfy_v2_test_tags_group_only(group, tag.lower()))
    return rows


class Timer:
    def __init__(self, author,
                 loops,
                 interval,
                 channel,
                 identifier,
                 group,
                 idol,
                 duration,
                 msg,
                 tags=None,
                 guild_id=None):
        self.identifier = identifier
        self.author = author
        self.loops = loops
        self.interval = interval
        self.channel = channel
        self.guild_id = guild_id
        self.group = group
        self.idol = idol
        self.duration = duration
        self.msg = msg
        self.tags = tags

    def destroy(self):
        self.loops = 0

    async def end_message(self):
        await self.channel.send(
            embed=discord.Embed(title=f"Timer: `{self.identifier}` of {self.group}'s {self.idol} has ended!",
                                description='',
                                color=discord.Color.blurple()))


class AuthorTimerList:
    def __init__(self, author):
        self.author = author
        self.timer_count = 1
        self.timers = []

    def add_timer(self, author, loops, interval, channel, interaction, group, idol, duration, msg, tags=None):
        if interaction.guild:
            timer = Timer(author,
                          loops,
                          interval,
                          channel,
                          self.timer_count,
                          group,
                          idol,
                          duration,
                          msg,
                          tags,
                          interaction.guild_id)
        else:
            timer = Timer(author,
                          loops,
                          interval,
                          channel,
                          self.timer_count,
                          group,
                          idol,
                          duration,
                          msg,
                          tags)
        self.timer_count += 1
        self.timers.append(timer)
        return timer

    def destroy_all_timers(self):
        self.timer_count -= len(self.timers)
        for timer in self.timers:
            timer.destroy()
        self.timers = []

    def destroy_timer(self, timer_id):
        for timer in self.timers:
            if timer.identifier == timer_id:
                self.timers.remove(timer)
                timer.destroy()
                self.timer_count -= 1
                return timer
        return

    def get_timers_info(self, author_name):
        info = []
        print(self.timers)
        for timer in self.timers:
            if timer.tags:
                creation_info = f"{timer.group} - {timer.idol}: {' '.join(timer.tags)}"
            else:
                creation_info = f"{timer.group} - {timer.idol}"
            info.append(f"""ID: `{timer.identifier}`\nCreation Information: `{creation_info}`
                        \nRemaining Duration: `{timedelta(seconds=(timer.loops * timer.interval))}`\n""")
        msg = "\n".join(info)
        return discord.Embed(title=f"Active Timers for {author_name}",
                             description=msg,
                             colour=discord.Color.blurple())


async def get_links_helper(interaction: discord.Interaction, group, idol, tags):
    group = group.lower()
    idol = idol.lower()
    g_id = find_group_id(group)
    if not g_id:
        await interaction.response.send_message(embed=error_embed(f'No group added named {group}!'))
        return
    m_id = find_member_id(g_id[0], idol)
    if not m_id:
        await interaction.response.send_message(embed=error_embed(f'No idol named {idol} in {group}!'))
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
            await interaction.response.send_message(
                embed=error_embed(f"No content for `{idol.title()}` in `{group}`!"))
            return
    return link_list, no_tag


async def group_picker(interaction: discord.Interaction, group_name: str):
    if not group_name:
        await interaction.response.send_autocomplete(pick_groups())
        return
    get_near_groups = [group for group in pick_groups(near=group_name) if group.lower().startswith(group_name.lower())]
    await interaction.response.send_autocomplete(get_near_groups)


async def idol_picker(interaction: discord.Interaction, idol_name: str):
    group = interaction.data['options'][0]['value']  # don't ask
    if not idol_name:
        await interaction.response.send_autocomplete(pick_group_members(group))
        return
    get_near_groups = [idol for idol in pick_group_members(group) if idol.lower().startswith(idol_name.lower())]
    await interaction.response.send_autocomplete(get_near_groups)


async def idol_picker_timer(interaction: discord.Interaction, idol_name: str):
    group = interaction.data['options'][1]['value']  # don't ask
    if not idol_name:
        await interaction.response.send_autocomplete(pick_group_members(group))
        return
    get_near_groups = [idol for idol in pick_group_members(group) if idol.lower().startswith(idol_name.lower())]
    await interaction.response.send_autocomplete(get_near_groups)


async def tag_picker(interaction: discord.Interaction, tag_name: str):
    if not tag_name:
        await interaction.response.send_autocomplete(pick_tags())
        return
    get_near_tags = [tag for tag in pick_tags(near=tag_name) if tag.lower().startswith(tag_name)]
    await interaction.response.send_autocomplete(get_near_tags)


class Fun(commands.Cog):
    """All the commands listed here are for gfys, images, or fancams.
    All groups with multiple word names are written as one word.
    """

    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        self.author_timers = []
        self.recent_posts = cache_dict["gfys"]["recent_posts"]
        self.VALID_LINK_GFY = ("https://gfycat.com",
                               "https://www.redgifs.com",
                               "https://www.gifdeliverynetwork.com")

    async def send_link_helper(self, interaction: discord.Interaction, group, idol, link_list, no_tag):
        if not link_list:
            await interaction.response.send_message(embed=error_embed(f"No fancams added for `{idol.title()}`!"))
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
                await interaction.response.send_message(embed=warning_embed(msg))
                await interaction.response.send_message(refine[0])
            else:
                await interaction.response.send_message(refine[0])
        else:
            crypto = SystemRandom()
            rand = crypto.randrange(len(refine) - 1)
            finale = refine[rand]
            self.recent_posts[group][idol].append(finale)
            if no_tag:
                msg = f'No content for requested tag(s): {", ".join(no_tag)}'
                await interaction.response.send_message(embed=warning_embed(msg))
                await interaction.response.send_message(finale)
            else:
                await interaction.response.send_message(finale)

    @discord.slash_command(
        name="image",
        description="get an image!"
    )
    @is_restricted()
    async def image(self, interaction: discord.Interaction, group, idol, *tags):
        """
        Sends an image from a specified group and idol
        Example: .image <group> <idol>
        This can be invoked with tags following <idol>
        Example .image <group> <idol> <tag> <tag>
        """
        link_list, no_tag = await get_links_helper(interaction, group, idol, tags)
        fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
        link_list = [x for x in link_list if x.endswith(fts)]
        await self.send_link_helper(interaction, group.lower(), idol.lower(), link_list, no_tag)

    # --- Fancam Commands --- #

    @discord.slash_command(
        name="fancam",
        description="get a fancam!"
    )
    @is_restricted()
    async def fancam(self, interaction: discord.Interaction, group, idol, *tags):
        """
        Get a fancam linked for a specified group and idol
        Example: .fancam <group> <idol>
        This can be invoked with tags following <idol>
        Example .fancam <group> <idol> <tag> <tag>
        """
        link_list, no_tag = await get_links_helper(interaction, group, idol, tags)
        yt_link = 'https://www.youtu'
        link_list = [x[0] for x in link_list if x[0].startswith(yt_link)]
        await self.send_link_helper(interaction, group.lower(), idol.lower(), link_list, no_tag)

    # --- Gfy/Link Commands --- #

    @discord.slash_command(name='addlink',
                           description="Add a link and contribute to Joy's database!")
    @is_restricted()
    @is_perma()
    async def addlink(
            self, interaction: discord.Interaction,
            group: str = SlashOption(
                name="group",
                description="Enter the group",
                required=True
            ),
            idol: str = SlashOption(
                name="idol",
                description="Enter the idol",
                required=True
            ),
            links_and_tags: str = SlashOption(
                name="links",
                description="Enter links followed by their tags"
            )
    ):
        """
        Adds a link to the idols list of gfys with tags following the link
        Example: .addlink <group> <idol> <link_1> <tag> <link_2> <tag> <tag>
        This will add the tags following the link, until the next link!
        If you wish to upload images, you can use discord's upload attachment
        or another external source. Please try to use an image source that
        embeds automatically in discord!
        """
        group = group.lower()
        idol = idol.lower()
        links = links_and_tags.split(" ")
        # if ctx.message.attachments:
        #     x = [x.url for x in ctx.message.attachments]
        #     links.extend(x)
        if not links:
            await interaction.response.send_message(embed=error_embed("No link(s) provided!"))
            return
        g_id = find_group_id(group)
        if not g_id:
            await interaction.response.send_message(embed=error_embed(f"{group} does not exist!"))
            return
        m_id = find_member_id(g_id[0], idol)
        if not m_id:
            await interaction.response.send_message(embed=error_embed(f"{idol} not in {group}!"))
            return
        author = interaction.user.id
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
            elif link.startswith("https://www.redgifs.com/") or link.startswith("https://redgifs.com/"):
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
            elif link.startswith("https://imgur.com/") or link.startswith("https://i.imgur.com/"):
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
                    await self.audit_channel(group, idol, str(link), interaction.user)
                    added_links += 1
                    last_added = currentlink
                else:
                    if currentlink == last_added:
                        continue
                    else:
                        duplicate_links += 1
        # loop end ..............................................................
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
        await interaction.response.send_message(embed=embed)

    def add_to_recent_posts(self, group, idol):
        if group not in self.recent_posts:
            updater = {group: {}}
            self.recent_posts.update(updater)
        if idol not in self.recent_posts[group]:
            updater = {idol: []}
            self.recent_posts[group].update(updater)

    def return_gfys(self, group, idol, tags=None):
        if tags:
            rows = rows_of_links_with_tags(group, tags, idol)
            if not rows:
                rows = rows_of_links(group, idol)
        else:
            rows = rows_of_links(group, idol)
        # row = (groupid, memberid, gromanname, mromanname, link)
        if len(rows) >= 1:
            return self.return_link_from_rows(rows)
        else:
            # handle error here
            error = send_gfy_error_formatting(group, idol)
            if error:
                return error_embed(error)

    def return_group_gfys(self, group, tags=None):
        if tags:
            rows = rows_of_links_with_tags(group, tags)
            if not rows:
                rows = rows_of_group_links(group)
        else:
            rows = rows_of_group_links(group)
        # row = (groupid, memberid, gromanname, mromanname, link)
        if len(rows) >= 1:
            return self.return_link_from_rows(rows)
        else:
            # handle error here
            error = send_gfy_error_formatting(group)
            if error:
                return error_embed(error)

    def return_link_from_rows(self, rows):
        """x: row: (gid, mid, gname, mname, link)"""
        links = []
        group = rows[0][3]
        idol = rows[0][4]
        for x in rows:
            group = x[2]
            idol = x[3]
            self.add_to_recent_posts(group, idol)
            if x[-1] not in self.recent_posts[x[2]][x[3]]:
                if x[-1].startswith(self.VALID_LINK_GFY):
                    links.append(x[-1])
        if not links:
            for x in rows:
                if x[-1].startswith(self.VALID_LINK_GFY):
                    links.append(x[-1])
                group = x[3]
                idol = x[4]
                self.add_to_recent_posts(group, idol)
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

    @discord.slash_command(name='gfy',
                           description="Get a gfy of your favourite idol!")
    @is_restricted()
    async def _gfyv2(self,
                     interaction: discord.Interaction,
                     group: str = SlashOption(
                         name="group",
                         description="Enter the group"
                     ),
                     idol: str = SlashOption(
                         name="idol",
                         description="Enter the idol",
                         required=False
                     ),
                     tag: str = SlashOption(
                         name="tag",
                         description="Enter an optional tag",
                         required=False)
                     ):
        """Returns a gfy from the requested group and idol!
        Examples: `.gfy <group> <idol>`, `.gfy RV Joy`
        You can also add tags after the idol arguement"""
        group = group.lower()
        if idol:
            idol = idol.lower()
            if tag:
                result = self.return_gfys(group, idol, [tag])
            else:
                result = self.return_gfys(group, idol)
        else:
            if tag:
                result = self.return_group_gfys(group, [tag])
            else:
                result = self.return_group_gfys(group)
        if isinstance(result, discord.Embed):
            # this is an error
            await interaction.response.send_message(embed=result)
        else:
            await interaction.response.send_message(result)

    # --- Random --- #

    @discord.slash_command(name='random',
                           description="Get a random gfy")
    @is_restricted()
    async def random(self, interaction: discord.Interaction):
        """Returns a random link, luck of the draw!"""

        async def random_link():
            link_member_group = random_link_from_links()
            link = link_member_group[0]
            idol = link_member_group[1]
            group = link_member_group[2]
            self.add_to_recent_posts(group, idol)
            if link not in self.recent_posts[group][idol]:
                self.recent_posts[group][idol].append(link)
                await interaction.response.send_message(f"Random choice! `{group.title()}`'s `{idol.title()}`\n{link}")
            else:
                relen = len(self.recent_posts[group][idol])
                gflen = member_link_count(group, idol)
                if relen == gflen:
                    print(f"resetting recent dict for {idol}")
                    self.recent_posts[group][idol] = []
                await random_link()

        await random_link()

    # --- Tags --- #

    @discord.slash_command(name='tags',
                           description="Returns a list of all tags")
    @is_restricted()
    async def tags(self, interaction: discord.Interaction):  # link=None
        """Returns a list of the tags!"""
        tag_list = [x[0] for x in get_all_tag_names() if len(x[0]) != 6 and not x[0].isdecimal()]
        msg = f"`{format_list(tag_list)}`\nSome tags have aliases, to check these try `.tagalias <tag>`\n" \
              f"Dates are also available, check out `.dates` to see them!"
        embed = discord.Embed(title="Tags:",
                              description=msg,
                              color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.slash_command(name='dates',
                           description="Returns a list of all date tags")
    @is_restricted()
    async def dates(self, interaction: discord.Interaction):
        date_list = [x[0] for x in get_all_tag_names() if len(x[0]) == 6 and x[0].isdecimal()]
        msg = f"`{format_list(date_list)}`"
        embed = discord.Embed(title="Dates:",
                              description=msg,
                              color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.slash_command(name='tagalias',
                           description="Returns the aliases on a tag")
    @is_restricted()
    async def tag_alias(self, interaction: discord.Interaction,
                        tag: str = SlashOption(
                            name="tag",
                            description="Enter a tag"
                        )):
        """Returns all aliases of a tag!"""
        tag = tag.lower()
        tag_name_and_id = get_tag_parent_from_alias(tag)
        tag_name = tag_name_and_id[0]
        tag_id = tag_name_and_id[-1]
        aliases = [x[0] for x in get_all_alias_of_tag(tag_id)]
        embed = discord.Embed(title=f"Aliases for `{tag_name}`:",
                              description=f"`{format_list(aliases)}`",
                              color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed)

    @discord.slash_command(name='taglink',
                           description="Add a tag to an existing link")
    @is_restricted()
    async def tag_link(self,
                       interaction: discord.Interaction,
                       tag: str = SlashOption(
                           name="tag",
                           description="the tag to add",
                           required=True
                       ),
                       link: str = SlashOption(
                           name="link",
                           description="the link to tag",
                           required=True
                       )):
        """
        Adds tag to links previously added.
        Example: .addtag <link> <tag> <tag>
        Example: .addtag <link> <tag> <link> <tag>
        """
        valid_tags = [x[0] for x in get_all_tag_alias_names()]
        author = interaction.user.id
        tag = tag.lower()
        tag = get_tag_parent_from_alias(tag)[0]
        if tag not in valid_tags:
            # check tag is a date format
            if tag.isdecimal() and len(tag) == 6:
                add_tag(tag, author)
                tag_id = find_tag_id(tag)
                add_tag_alias(tag_id, tag, author)
                added_tagged_link = add_link_tags(link, tag)
                if added_tagged_link:
                    interaction.response.send_message(
                        embed=success_embed(f'Added tag: {tag} to link {link}'))
                    return
        else:
            added = add_link_tags(link, tag)
            if added:
                interaction.response.send_message(
                    embed=success_embed(f'Added tag: {tag} to link {link}'))
                return
        await interaction.response.send_message(embed=error_embed(f'failed to add tag: {tag} to link!'))

    @discord.slash_command(name='tagged',
                           description='Get a gfy with a specific tag!')
    @is_restricted()
    async def tagged(self, interaction: discord.Interaction,
                     tag: str = SlashOption(
                         name='tag',
                         description='Enter a tag'
                     )):
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
            await interaction.response.send_message(f"Tagged `{tag}`, {finale}")
        else:
            await interaction.response.send_message(f"Nothing for tag `{tag}`")

    @discord.slash_command(name='taggedimage',
                           description="get an image with a tag!")
    @is_restricted()
    async def taggedimage(self, interaction: discord.Interaction,
                          tag: str = SlashOption(
                              name="tag",
                              description="the tag you wish for"
                          )):
        """
        Sends a random image with the specified tag.
        Example: .taggedimage <tag>
        """
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
            await interaction.response.send_message(f"Tagged `{tag}`, {finale}")
        else:
            await interaction.response.send_message(f"Nothing for tag `{tag}`")

    @discord.slash_command(name='taggedgfy',
                           description="get a tagged gfy")
    @is_restricted()
    async def taggedgfy(self,
                        interaction: discord.Interaction,
                        tag: str = SlashOption(
                            name="tag",
                            description="the tag you wish for"
                        )):
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
            await interaction.response.send_message(f"Tagged `{tag}`, {finale}")
        else:
            await interaction.response.send_message(f"Nothing for tag `{tag}`")

    @discord.slash_command(name='taggedfancam',
                           description="get a tagged fancam")
    @is_restricted()
    async def taggedfancam(self,
                           interaction: discord.Interaction,
                           tag: str = SlashOption(
                               name="tag",
                               description="the tag you wish for"
                           )):
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
            await interaction.response.send_message(f"Tagged `{tag}`, {finale}")
        else:
            await interaction.response.send_message(f"Nothing for tag `{tag}`")

    # --- Timer Commands --- #

    # TODO take a good look at making this as easy as possible
    # TODO also ensure that the idol value can be none
    # TODO ensure autocomplete is added to all values
    @discord.slash_command(name='timer',
                           description="Joy will send you links for a short duration.")
    @is_restricted()
    async def _timer(self,
                     interaction: discord.Interaction,
                     duration,
                     group,
                     idol,
                     interval=10,
                     tags='none'):
        duration = int(duration)
        if not interval:
            interval = 10
        interval = int(interval)
        if interval < 10:
            interval = 10
        tags = tags.split(" ")
        if tags[0].lower() == 'none':
            tags = None
        msg = None
        if interaction.guild:
            max_duration = get_guild_max_duration(interaction.guild_id)
            if max_duration:
                if duration > max_duration[0]:
                    duration = max_duration[0]
                    msg = f'\nDuration reduced to server max duration of `{max_duration[0]}`.'
        if tags:
            links = rows_of_links_with_tags(group, tags, idol)
        else:
            links = rows_of_links(group, idol)
        loops = (abs(duration) * 60) // abs(interval)
        if len(links) < loops:
            loops = len(links)
        author = interaction.user.id
        channel = await self.disclient.fetch_channel(interaction.channel_id)
        for author_timer_list in self.author_timers:
            if author_timer_list.author == author:
                timer = author_timer_list.add_timer(author,
                                                    loops,
                                                    interval,
                                                    channel,
                                                    interaction,
                                                    group,
                                                    idol,
                                                    duration,
                                                    msg,
                                                    tags)
                if msg:
                    msg = f"{timer.group}'s {timer.idol} for {timer.duration} minute(s)! {msg}\n" \
                          f"Timer ID: `{timer.identifier}`"
                else:
                    msg = f"{timer.group}'s {timer.idol} for {timer.duration} minute(s)!" \
                          f"\nTimer ID: `{timer.identifier}`"
                await interaction.response.send_message(embed=discord.Embed(title='Starting Timer!',
                                                        description=msg,
                                                        color=discord.Color.blurple()))
                await self.timer_helper(timer, links)
                return  # author already has timers running
        author_timer_list: AuthorTimerList = AuthorTimerList(author)
        self.author_timers.append(author_timer_list)
        timer = author_timer_list.add_timer(author,
                                            loops,
                                            interval,
                                            channel,
                                            interaction,
                                            group,
                                            idol,
                                            duration,
                                            msg,
                                            tags)
        if msg:
            msg = f"{timer.group}'s {timer.idol} for {timer.duration} minute(s)! {msg}\nTimer ID: `{timer.identifier}`"
        else:
            msg = f"{timer.group}'s {timer.idol} for {timer.duration} minute(s)!\nTimer ID: `{timer.identifier}`"
        await interaction.response.send_message(embed=discord.Embed(title='Starting Timer!',
                                                description=msg,
                                                color=discord.Color.blurple()))
        await self.timer_helper(timer, links)

    async def timer_helper(self, timer: Timer, links):
        while timer.loops > 0:
            print(timer.channel)
            channel = timer.channel
            await channel.send(self.return_link_from_rows(links))
            timer.loops -= 1
            if timer.loops <= 0:
                await timer.end_message()
                return
            await asyncio.sleep(timer.interval)

    @discord.slash_command(name='viewtimers',
                           description='View all of the info on your active timers')
    @is_restricted()
    async def view_timers(self, interaction: discord.Interaction):
        author = interaction.user.id
        for author_timer in self.author_timers:
            if author_timer.author == author:
                e = author_timer.get_timers_info(interaction.user.name)
                await interaction.response.send_message(embed=e)
                return

        await interaction.response.send_message(embed=error_embed(f"No timers active for {interaction.user.name}!"))

    @discord.slash_command(name='stoptimer',
                           description="Stop a timer you previously created")
    @is_restricted()
    async def stop_timer(self, interaction: discord.Interaction, timer_id):
        """
        Stops the timer function by user, if you have multiple timers running, specify the timer number.
        You can stop all timers with: .stop all
        """
        author = interaction.user.id
        for author_timer in self.author_timers:
            if author_timer.author == author:
                if timer_id.lower() == 'all':
                    author_timer.destroy_all_timers()
                    await interaction.response.send_message(
                        f"Destroyed all timers for {interaction.user.name}"
                    )
                    return
                else:
                    timer = author_timer.destroy_timer(int(timer_id))
                    if timer:
                        await interaction.response.send_message(
                            f"Timer: `{timer.identifier}` of {timer.group}'s - {timer.idol} successfully stopped.")
                    else:
                        await interaction.response.send_message(
                            f"No timer found with ID: {timer_id} from {interaction.user.name}!", ephemeral=True)
                    return
        await interaction.response.send_message(f"No timers running for {interaction.user.name}")

    @discord.slash_command(name='forcestoptimer',
                           description="Stop a members timers (all) in your server.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @is_restricted()
    async def _destroy_timers(self, interaction: discord.Interaction, member: discord.Member):
        """Force all timers started by a user to end.
        Usage (invoke this command in the same channel that the timer is running):
        .force_stop @<user>
        .force_stop <User ID>"""
        destroyed = 0
        for author_timer in self.author_timers:
            if author_timer.author == member.id:
                for timer in author_timer.timers:
                    if timer.guild_id == interaction.guild_id:
                        timer.destroy()
                        del timer
                        destroyed += 1
        if destroyed > 0:
            await interaction.response.send_message(f"Successfully destroyed {destroyed} timers from {member.mention}.")
        else:
            await interaction.response.send_message(f"No timers from {member.mention} in {interaction.guild}.",
                                                    ephemeral=True)

    # --- Info Commands --- #

    # @commands.command()
    @discord.slash_command(name='info',
                           description="Get info on groups, a group, or an idol")
    @is_restricted()
    async def info(
            self, interaction: discord.Interaction,
            group: str = SlashOption(
                name="group",
                description="Enter the group",
                required=False
            ),
            idol: str = SlashOption(
                name="idol",
                description="Enter the idol",
                required=False
            ),
    ):
        """
        returns info about the groups added to the bot,
        or the group specified, or the idol specified.
        Example: .info
        Example: .info <group>
        Example: .info <group> <idol>
        """
        if not group:
            groups = get_groups()
            groups = [x[0] for x in groups]
            group_msg = f"`{format_list(groups)}`"
            s = """Try `/info group:<group>` for more information on that group!\n
                   Try `/info group:<group> idol:<idol>` for me information on that idol!"""
            embed = discord.Embed(title='Groups:',
                                  description=group_msg + '\n\n' + s,
                                  color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed)
        elif group and not idol:
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
                await interaction.response.send_message(embed=embed)
            elif name_and_g_id is None:
                await interaction.response.send_message(
                    embed=error_embed(f'No group called {group}!\nTry `.info` to see a list of groups!'))
        elif idol and group:
            idol = idol.lower()
            group = group.lower()
            g_id_and_name = find_group_id_and_name(group)
            if not g_id_and_name:
                await interaction.response.send_message(embed=error_embed(f"No group called {group}!"))
                return
            g_id = g_id_and_name[0]
            g_name = g_id_and_name[-1]
            m_id_and_name = find_member_id_and_name(g_id, idol)
            if not m_id_and_name:
                await interaction.response.send_message(embed=error_embed(f"No idol called {idol} in {group}!"))
                return
            m_id = m_id_and_name[0]
            m_name = m_id_and_name[-1]
            links = get_member_links(m_id)
            link_count = len(links)
            fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
            pic_links_count = len([x[0] for x in links if x[0].endswith(fts)])
            member_aliases = [x[0] for x in find_member_aliases(m_id)]
            is_tagged = []
            tags_and_count = get_all_tags_on_member_and_count(m_id)
            total_tagged_links = 0
            for tags in tags_and_count:
                total_tagged_links += tags[1]
                is_tagged.append(f"{tags[0]}: {tags[1]}")
            a = f'{g_name} {m_name.title()} Information'
            d = hide_links([x[0] for x in last_three_links(m_id)])
            untagged_count = int(link_count) - total_tagged_links
            if untagged_count < 0:
                untagged_count = 0
            if is_tagged:
                c = format_list(is_tagged)
                if pic_links_count > 1 or pic_links_count == 0:
                    s = (f'`{m_name.title()}` has a total of `{link_count}` link(s)!\n'
                         f'Out of these links, `{pic_links_count}` are images.\n'
                         f'**Alias(es):** `{"`, `".join(member_aliases)}`\n'
                         f'**Tags:** `{c}`\n'
                         f'**Untagged:** {untagged_count}')
                else:
                    s = (f'`{m_name.title()}` has a total of `{link_count}` link(s)!\n'
                         f'Out of these links, there is only `{pic_links_count}` image.\n'
                         f'**Alias(es):** `{"`, `".join(member_aliases)}`\n'
                         f'**Tags:** `{c}`\n'
                         f'**Untagged:** {untagged_count}')
            else:
                s = (f'`{m_name.title()}` has `{link_count}` link(s)!\n'
                     f'Out of these links, `{pic_links_count}` are images.\n'
                     f'**Alias(es):** {format_list(member_aliases)}\n'
                     f'**Untagged:** {untagged_count}')
            if d:
                s = s + f'\nThe last 3 links added:\n<{d}>'

            embed = discord.Embed(title=f'**{a}**',
                                  description=s,
                                  color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=error_embed(f"No group named `{group}`!"))

    @info.on_autocomplete("group")
    @_gfyv2.on_autocomplete("group")
    @addlink.on_autocomplete("group")
    @_timer.on_autocomplete("group")
    async def _group(self, interaction: discord.Interaction, group_name: str):
        await group_picker(interaction, group_name)

    @info.on_autocomplete("idol")
    @_gfyv2.on_autocomplete("idol")
    @addlink.on_autocomplete("idol")
    async def _idol_picker(self, interaction: discord.Interaction, idol_name: str):
        await idol_picker(interaction, idol_name)

    @_timer.on_autocomplete("idol")
    async def _idol_picker_timer(self, interaction: discord.Interaction, idol_name: str):
        await idol_picker_timer(interaction, idol_name)

    @tag_alias.on_autocomplete("tag")
    @tagged.on_autocomplete("tag")
    @tag_link.on_autocomplete("tag")
    @taggedimage.on_autocomplete("tag")
    @taggedgfy.on_autocomplete("tag")
    @taggedfancam.on_autocomplete("tag")
    async def _tag_picker(self, interaction: discord.Interaction, tag_name: str):
        await tag_picker(interaction, tag_name)

    @_gfyv2.on_autocomplete("tag")
    async def _tag_on_idol_picker(self, interaction: discord.Interaction, tag_name: str):
        group = interaction.data['options'][0]['value']
        idol = interaction.data['options'][1]['value']
        if not tag_name:
            await interaction.response.send_autocomplete(pick_tags_on_idol(group, idol))
            return
        get_near_tags = [tag for tag in pick_tags_on_idol(group, idol, near=tag_name.lower()) if tag.lower().startswith(tag_name.lower())]
        await interaction.response.send_autocomplete(get_near_tags)

    @discord.slash_command(name='totallinks',
                           description="Get the total number of links added to Joy")
    @is_restricted()
    async def totallinks(self, interaction: discord.Interaction):
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
        await interaction.response.send_message(embed=embed)

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
        main_audcha = await self.disclient.fetch_channel(apis_dict["auditing_channel"])
        s = f'Time Added: `{dt}`\nUser ID: `{author.id}`\nGroup: `{group}`\nIdol: `{idol}`\nLink: {link}'
        embed = discord.Embed(title=s,
                              color=discord.Color.blurple())
        embed.set_footer(text=f"Added by {author}",
                         icon_url=author.avatar.url)
        try:
            await main_audcha.send(embed=embed)
            await main_audcha.send(link)
        except Exception as e:
            print("can't send to auditing channel")
            print(e)
        aud_chas = get_auditing_channels()
        if aud_chas:
            list_of_chas = [x[0] for x in aud_chas]
            for chan in list_of_chas:
                try:
                    channel = await self.disclient.fetch_channel(int(chan))
                except Exception as e:
                    print("probably forbidden")
                    continue
                fstr = f'Added: `{group}`, `{idol}`: {link}'
                try:
                    await channel.send(fstr)
                except AttributeError or nextcord.errors.Forbidden:
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
