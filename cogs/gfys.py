import discord
from discord.ext import commands
import random
import json
import asyncio
from data import direc_dict
from data import gfys_dict
from data import recent_dict
from data import contri_dict
from data import auditing_dict


class Fun(commands.Cog):
    """All of the commands listed here are for gfys, images, or fancams.
    All groups with multiple word names are written as one word.
    Example: Red Velvet will become RedVelvet
    """
    def __init__(self, disclient):
        self.disclient = disclient
        self.loops = {}
        self.disclient.loop.create_task(self.write_gfys())
        self.disclient.loop.create_task(self.write_contri())
        self.disclient.loop.create_task(self.write_recent())

    @commands.Cog.listener()
    async def write_recent(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["recents"], 'w') as rece:
                json.dump(recent_dict, rece, indent=4)
            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def write_contri(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["contri"], 'w') as cont:
                json.dump(contri_dict, cont, indent=4)
            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def write_gfys(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["gfys"], 'w') as gfys:
                json.dump(gfys_dict, gfys, indent=4)
            await asyncio.sleep(5)

    @commands.command()
    async def image(self, ctx, group, idol, *tags):
        """
        Sends an image from a specified group and idol
        Example: .image <group> <idol>
        This can be invoked with tags following <idol>
        Example .image <group> <idol> <tag> <tag>
        """
        grp = group.lower()
        idl = idol.lower()
        if tags:
            tags = tags
        else:
            tags = None
        if grp in gfys_dict["groups"]:
            if idl in gfys_dict["groups"][grp]:
                fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
                if tags:
                    tagged_list = []
                    for tag in tags:
                        if tag in gfys_dict["tags"]:
                            can_send = []
                            for element in gfys_dict["tags"][tag]:
                                if element.endswith(fts):
                                    tagged_list.append(element)
                                elif 'twimg' in element:
                                    tagged_list.append(element)
                            for image in gfys_dict["groups"][grp][idl]:
                                if image in tagged_list:
                                    can_send.append(image)
                            await ctx.send(random.choice(can_send))
                        else:
                            await ctx.send(
                                    f"Nothing tagged {tag} for {idl}")
                else:
                    c_s = []
                    for element in gfys_dict["groups"][grp][idl]:
                        if element.endswith(fts):
                            c_s.append(element)
                        elif 'twimg' in element:
                            c_s.append(element)
                    if grp not in recent_dict:
                        updater = {grp: {}}
                        recent_dict.update(updater)
                    if idl not in recent_dict[grp]:
                        updater = {idl: []}
                        recent_dict[grp].update(updater)
                    refine = [x for x in c_s if x not in recent_dict[grp][idl]]
                    if len(refine) <= 1:
                        print(f"resetting {grp}: {idl} list.")
                        recent_dict[grp][idl] = []
                        refine = c_s
                    finale = random.choice(refine)
                    recent_dict[grp][idl].append(finale)
                    await ctx.send(finale)
            else:
                await ctx.send(f"Nothing for {idol} in {group}.")
        else:
            await ctx.send(f"Nothing for {group}")

    @commands.command()
    async def addimage(self, ctx, group, idol, *args):
        """
        Add and image to specified idol
        Example: .addimage <group> <idol> <link_1> <tag> <link_2> <tag> <tag>
        This will add the tags following the link, until the next link!
        If the image is a discord attachment, it will only take the first one
        """
        group = group.lower()
        idol = idol.lower()
        links = list(args)
        if ctx.message.attachments:
            links.append(ctx.message.attachments[0].url)
        if not links:
            await ctx.send("No link(s) provided!")
        else:
            fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
            currentlink = []
            for link in links:
                if link.endswith(fts):
                    try:
                        currentlink.pop()
                    except IndexError:
                        print("no pop")
                    currentlink.append(link)
                elif "twimg" in link:
                    try:
                        currentlink.pop()
                    except IndexError:
                        print("no pop")
                    split_link = link.split("/")
                    if "?" in split_link[-1]:
                        splitt = split_link[-1].split("?")
                        if "png" in splitt[-1]:
                            newending = splitt[0] + "?format=png&name=orig"
                        else:
                            newending = splitt[0] + "?format=jpg&name=orig"
                        link = "https://pbs.twimg.com/media/" + str(newending)
                    elif "." in split_link[-1]:
                        splitt = split_link[-1].split(".")
                        if "png" in splitt[-1]:
                            newending = splitt[0] + "?format=png&name=orig"
                        else:
                            newending = splitt[0] + "?format=jpg&name=orig"
                        link = split_link[:-1] + newending
                    currentlink.append(link)
                else:
                    link = link.lower()
                    if link not in gfys_dict["tags"]:
                        updater = {str(link): []}
                        gfys_dict["tags"].update(updater)
                        gfys_dict["tags"][link].append(str(currentlink[0]))
                        await ctx.send(f"Added image to `{link}` tag!")
                        continue
                    else:
                        if str(currentlink[0]) not in gfys_dict["tags"][link]:
                            author = str(ctx.author.id)
                            if author not in contri_dict:
                                print(f"Added {author} to Contributers")
                                contri_dict[author] = {}
                                contri_dict[author]['cont'] = 0
                            contri_dict[author]['cont'] += 1
                            gfys_dict["tags"][link].append(str(currentlink[0]))
                            await ctx.send(f"Added to the `{link}` tag!")
                            continue
                        else:
                            await ctx.send(f"Already added to `{link}` tag!")
                            continue
                if str(link) not in gfys_dict["groups"][group][idol]:
                    gfys_dict["groups"][group][idol].append(str(link))
                    auth = ctx.author
                    await self.audit_channel(group, idol, str(link), auth)
                    await ctx.send(f"Added to `{group}`'s `{idol.title()}`!")
                else:
                    await ctx.send("Already added!")

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
        if tags:
            tags = tags
        else:
            tags = None
        if group in gfys_dict["groups"]:
            if idol in gfys_dict["groups"][group]:
                if tags:
                    tagged_list = []
                    for tag in tags:
                        if tag in gfys_dict["tags"]:
                            can_send = []
                            for element in gfys_dict["tags"][tag]:
                                if element.startswith("https://www.youtu"):
                                    tagged_list.append(element)
                            for fancam in gfys_dict["groups"][group][idol]:
                                if fancam in tagged_list:
                                    can_send.append(fancam)
                            await ctx.send(random.choice(can_send))
                        else:
                            await ctx.send(
                                    f"Nothing tagged {tag} for {idol}")
                else:
                    can_send = []
                    for fancam in gfys_dict["groups"][group][idol]:
                        if fancam.startswith("https://www.youtu"):
                            can_send.append(fancam)
                    await ctx.send(random.choice(can_send))
            else:
                await ctx.send(f"Nothing for {idol} in {group}.")
        else:
            await ctx.send(f"Nothing for {group}")

    @commands.command()
    async def addfancam(self, ctx, group, idol, *args):
        """
        Add a fancam to a specified idol in a group
        Example: .addfancam <group> <idol> <link_1> <tag> <link_2> <tag> <tag>
        This will add the tags following the link, until the next link!
        """
        group = group.lower()
        idol = idol.lower()
        links = args
        if not links:
            await ctx.send("No link(s) provided!")
        else:
            currentlink = []
            for link in links:
                if link.startswith("https://www.youtu"):
                    try:
                        currentlink.pop()
                    except IndexError:
                        print("index error")
                    currentlink.append(link)
                else:
                    link = link.lower()
                    if link not in gfys_dict["tags"]:
                        updater = {str(link): []}
                        gfys_dict["tags"].update(updater)
                        gfys_dict["tags"][link].append(str(currentlink[0]))
                        await ctx.send(f"Added fancam to `{link}` tag!")
                        continue
                    else:
                        if str(currentlink[0]) not in gfys_dict["tags"][link]:
                            gfys_dict["tags"][link].append(str(currentlink[0]))
                            await ctx.send(f"Added to the `{link}` tag!")
                            continue
                        else:
                            await ctx.send(f"Already added to `{link}` tag!")
                            continue
                if str(link) not in gfys_dict["groups"][group][idol]:
                    author = str(ctx.author.id)
                    if author not in contri_dict:
                        print(f"Added {author} to Contributers")
                        contri_dict[author] = {}
                        contri_dict[author]['cont'] = 0
                    contri_dict[author]['cont'] += 1
                    gfys_dict["groups"][group][idol].append(str(link))
                    auth = ctx.author
                    await self.audit_channel(group, idol, str(link), auth)
                    await ctx.send(f"Added to `{group}`'s `{idol.title()}`!")
                else:
                    await ctx.send("Already added!")

# --- Gfy Commands --- #

    @commands.command()
    async def addgfy(self, ctx, group, idol, *args):
        """
        Adds a gfy to the idols list of gfys with tags following the link
        Example: .addgfy <group> <idol> <link_1> <tag> <link_2> <tag> <tag>
        This will add the tags following the link, until the next link!
        """
        group = group.lower()
        idol = idol.lower()
        links = args
        if not links:
            await ctx.send("No link(s) provided!")
        elif group not in gfys_dict["groups"]:
            msg = f"{group} does not exist!"
            embed = discord.Embed(title="Error",
                                  description=msg,
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        elif idol not in gfys_dict["groups"][group]:
            msg = f"{idol} not in {group}!"
            embed = discord.Embed(title="Error",
                                  description=msg,
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            currentlink = None
            send_message = {}
            i = 0
            d = 0
            dt = 0
            it = 0
            for gfy in links:
                if gfy.endswith("/"):
                    gfy = gfy[:-1]
                if gfy.startswith("https://gfycat.com/"):
                    split = gfy.split("/")
                    if "-" in split[-1]:
                        split[-1] = split[-1].split("-")
                        split[-1] = split[-1][0]
                    gfy = "https://gfycat.com/" + split[-1]
                    currentlink = gfy
                elif gfy.startswith("https://www.redgifs.com/"):
                    split = gfy.split("/")
                    gfy = "https://www.redgifs.com/watch/" + split[-1]
                    currentlink = gfy
                elif gfy.startswith("https://www.gifdeliverynetwork.com/"):
                    split = gfy.split("/")
                    gfy = "https://www.gifdeliverynetwork.com/" + split[-1]
                    currentlink = gfy
                else:
                    gfy = gfy.lower()
                    if gfy not in gfys_dict["tags"]:
                        updater = {str(gfy): []}
                        gfys_dict["tags"].update(updater)
                        gfys_dict["tags"][gfy].append(str(currentlink))
                        it += 1
                        if gfy not in send_message:
                            send_message.update({gfy: 1})
                        else:
                            send_message[gfy] += 1
                        continue
                    else:
                        if not currentlink:
                            continue
                        elif currentlink not in gfys_dict["tags"][gfy]:
                            gfys_dict["tags"][gfy].append(currentlink)
                            it += 1
                            if gfy not in send_message:
                                send_message.update({gfy: 1})
                            else:
                                send_message[gfy] += 1
                            continue
                        else:
                            dt += 1
                            continue
                if str(gfy) not in gfys_dict["groups"][group][idol]:
                    gfys_dict["groups"][group][idol].append(str(gfy))
                    await self.audit_channel(group, idol, str(gfy), ctx.author)
                    i += 1
                else:
                    d += 1
            if i > 0:
                idol = idol.title()
                await ctx.send(
                        f"Added `{i}` link(s) to `{group}`'s `{idol}`!")
                author = str(ctx.author.id)
                if author not in contri_dict:
                    print(f"Added {author} to Contributers")
                    contri_dict[author] = {}
                    contri_dict[author]['cont'] = 0
                contri_dict[author]['cont'] += i
            if it > 0:
                lets = []
                for key, value in send_message.items():
                    lets.append("{}: {}".format(key, value))
                await ctx.send(
                        f"Added tagged links to: `{format_list(lets)}`.")
            if d > 0:
                await ctx.send(f"Skipped adding `{d}` duplicate link(s).")
            if dt > 0:
                await ctx.send(
                        f"Skipped adding `{dt}` duplicate link(s) to tags.")

    @commands.command()
    async def gfy(self, ctx, group, idol, *tags):
        """
        Sends a gfy of the specified idol
        Example: .gfy <group> <idol>
        This can be invoked with tags following <idol>
        Example .gfy <group> <idol> <tag> <tag>
        """
        grp = group.lower()
        idl = idol.lower()
        if tags:
            tags = tags
        else:
            tags = None
        if grp in gfys_dict["groups"]:
            group_dict = gfys_dict["groups"][grp]
            if idl in group_dict:
                to_sent = []
                r_s = []
                for elem in gfys_dict["groups"][grp][idl]:
                    valid_links = (
                        "https://gfycat.com/",
                        "https://www.redgifs.com/",
                        "https://www.gifdeliverynetwork.com/"
                    )
                    try:
                        if elem.startswith(valid_links):
                            to_sent.append(elem)
                    except IndexError:
                        await ctx.send(f"No content for {idl}")
                        break
                if tags:
                    for tag in tags:
                        for element in gfys_dict["tags"][tag]:
                            try:
                                if element in to_sent:
                                    r_s.append(element)
                            except IndexError:
                                t = tag
                                await ctx.send(
                                    f"No content with {t} tag for {idl}.")
                                break
                else:
                    r_s = to_sent
                if grp not in recent_dict:
                    updater = {grp: {}}
                    recent_dict.update(updater)
                if idl not in recent_dict[grp]:
                    updater = {idl: []}
                    recent_dict[grp].update(updater)
                refine = [x for x in r_s if x not in recent_dict[grp][idl]]
                if len(refine) <= 1:
                    print(f"resetting {grp}: {idl} list.")
                    recent_dict[grp][idl] = []
                    refine = r_s
                finale = random.choice(refine)
                recent_dict[grp][idl].append(finale)
                await ctx.send(finale)
            else:
                await ctx.send(
                    f"No content for `{idl.title()}` in `{grp}`")
        else:
            await ctx.send(f"No content for `{grp}`.")

# --- Random --- #

    @commands.command(aliases=['r'])
    async def random(self, ctx):
        """Returns a random link, luck of the draw!"""
        async def random_recur():
            grp = random.choice(list(gfys_dict["groups"].keys()))
            idl = random.choice(list(gfys_dict["groups"][grp].keys()))
            try:
                fi = random.choice(gfys_dict["groups"][grp][idl])
            except IndexError:
                await random_recur()
            if grp not in recent_dict:
                updater = {grp: {}}
                recent_dict.update(updater)
            if idl not in recent_dict[grp]:
                updater = {idl: []}
                recent_dict[grp].update(updater)
            if fi in recent_dict[grp][idl]:
                relen = len(recent_dict[grp][idl])
                gflen = len(gfys_dict["groups"][grp][idl])
                if relen == gflen:
                    print(f"resetting recent dict for {idl}")
                    recent_dict[grp][idl] = []
                await random_recur()
            else:
                recent_dict[grp][idl].append(fi)
                await ctx.send(
                    f"Random choice! `{grp.title()}`'s `{idl.title()}` {fi}")
        await random_recur()

# --- Tags --- #

    @commands.command()
    async def tags(self, ctx):  # link=None
        """Returns a list of the tags"""
        sub_dict = gfys_dict["tags"]
        await ctx.send(f"Tags: `{format_list(sub_dict.keys())}`")

    @commands.command()
    async def addtag(self, ctx, *tags_or_links):
        """
        Adds tag to links previously added
        Example: .addtag <link> <tag> <tag>
        Example: .addtag <link> <tag> <link> <tag>
        """
        tags_list = tags_or_links
        currentlink = []
        a = 0
        b = 0
        for tag in tags_list:
            valid_links = (
                "https://gfycat.com/",
                "https://www.redgifs.com/",
                "https://www.gifdeliverynetwork.com/",
                "https://pbs.twimg.com/media/",
                "https://youtu",
                "https://www.youtu"
            )
            valid_fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
            if tag.startswith(valid_links):
                try:
                    currentlink.pop()
                except IndexError:
                    print("nothing to pop")
                currentlink.append(tag)
            elif tag.endswith(valid_fts):
                try:
                    currentlink.pop()
                except IndexError:
                    print("nothing to pop")
                currentlink.append(tag)
            else:
                tag = tag.lower()
                if tag not in gfys_dict["tags"]:
                    updater = {str(tag).lower(): []}
                    gfys_dict["tags"].update(updater)
                if currentlink[0] not in gfys_dict["tags"][tag]:
                    gfys_dict["tags"][tag].append(currentlink[0])
                    a += 1
                else:
                    b += 1
        if a > 0:
            await ctx.send(f"Added tags to {a} links!")
        if b > 0:
            await ctx.send(
                    f"Skipped adding tags to {b} links, tags already exist.")

    @commands.command(aliases=['t'])
    async def tagged(self, ctx, tag):
        """
        Sends a random gfy with the specified tag
        Example: .tagged <tag>
        """
        tag = tag.lower()
        if tag in gfys_dict["tags"]:
            if tag not in recent_dict:
                updater = {tag: []}
                recent_dict.update(updater)
            taggfy = gfys_dict["tags"][tag]
            recentag = recent_dict[tag]
            refine = [x for x in taggfy if x not in recentag]
            if len(refine) <= 1:
                recent_dict[tag] = []
                refine = gfys_dict["tags"][tag]
            choice = random.choice(refine)
            await ctx.send(f"Tagged `{tag}`, {choice}")
            recent_dict[tag].append(choice)
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['ti'])
    async def taggedimage(self, ctx, tag):
        """
        Sends a random image with the specified tag
        Example: .taggedimage <tag>
        """
        tag = tag.lower()
        if tag in gfys_dict["tags"]:
            can_send = []
            valid_fts = (".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")
            for element in gfys_dict["tags"][tag]:
                if element.endswith(valid_fts):
                    can_send.append(element)
                if element.startswith("https://pbs.twimg"):
                    can_send.append(element)
            if tag not in recent_dict:
                updater = {tag: []}
                recent_dict.update(updater)
            refine = [x for x in can_send if x not in recent_dict[tag]]
            if len(refine) <= 1:
                recent_dict[tag] = []
            choice = random.choice(refine)
            recent_dict[tag].append(choice)
            await ctx.send(f"Tagged `{tag}`, {choice}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['tg'])
    async def taggedgfy(self, ctx, tag):
        """
        Sends a random gfy with the specified tag
        Example: .taggedgfy <tag>
        """
        tag = tag.lower()
        if tag in gfys_dict["tags"]:
            can_send = []
            valid_links = (
                "https://www.redgifs",
                "https://gfy",
                "https://gifdeliverynetwork"
            )
            for element in gfys_dict["tags"][tag]:
                if element.startswith(valid_links):
                    can_send.append(element)
            if tag not in recent_dict:
                updater = {tag: []}
                recent_dict.update(updater)
            refine = [x for x in can_send if x not in recent_dict[tag]]
            if len(refine) <= 1:
                recent_dict[tag] = []
            choice = random.choice(refine)
            recent_dict[tag].append(choice)
            await ctx.send(f"Tagged `{tag}`, {choice}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

    @commands.command(aliases=['tf'])
    async def taggedfancam(self, ctx, tag):
        """Sends a random fancam with the specified tag"""
        tag = tag.lower()
        if tag in gfys_dict["tags"]:
            can_send = []
            valid_links = (
                "https://youtu",
                "https://www.youtu"
            )
            for element in gfys_dict["tags"][tag]:
                if element.startswith(valid_links):
                    can_send.append(element)
            if tag not in recent_dict:
                updater = {tag: []}
                recent_dict.update(updater)
            refine = [x for x in can_send if x not in recent_dict[tag]]
            if len(refine) <= 1:
                recent_dict[tag] = []
            choice = random.choice(refine)
            recent_dict[tag].append(choice)
            await ctx.send(f"Tagged `{tag}`, {choice}")
        else:
            await ctx.send(f"Nothing for tag `{tag}`")

# --- Adding Groups and Idols --- #

# --- Timer Commands --- #

    @commands.command(aliases=['nohands'])
    async def timer(self, ctx, duration, interval, group, idol, *tags):
        """
        Sends a gfy in the channel every user defined interval in seconds
        (minimum is 10 seconds) for a duration (maximum of 30 minutes) of time.
        When calling state the duration in minutes, and the interval in seconds
        Example: .timer <duration(min)> <interval(sec)> <group> <idol>
        Example: .timer 10 10 RedVelvet Joy
        This command can also be invoked with tags after <idol> add, <tag>
        """
        await self.disclient.wait_until_ready()
        if group not in gfys_dict["groups"]:
            await ctx.send(f"Nothing for {group}")
        elif idol not in gfys_dict["groups"][group]:
            await ctx.send(f"Nothing for {idol} in {group}")
        else:
            interval = int(interval)
            duration = int(duration)
            if interval <= 10:
                interval = 10
            if duration >= 30:
                duration = 30
            loops = int((duration * 60) / interval)
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
            while self.loops[author] > 0:
                await self.gfy(ctx, group, idol, *tags)
                self.loops[author] -= 1
                if self.loops[author] <= 0:
                    await ctx.send("Timer finished.")
                    del self.loops[author]
                await asyncio.sleep(interval)

    @commands.command(aliases=['stop'])
    async def stop_timer(self, ctx, timer_number=None):
        """
        Stops the timer function by user, if you have
        multiple timers running, specify the timer number.
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
        #  doesn't work at "all"
        if str(timer_number) == 'all':
            i = 0
            for element in checklist:
                self.loops[element] = 0
                del self.loops[element]
                i += 1
            await ctx.send(f"Stopped all {i} timers for `{author}`")
        elif len(checklist) == 1:
            self.loops[checklist[0]] = 0
            del self.loops[checklist[0]]
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
            del self.loops[author]
            print(f"deleted {author} from loops")
        else:
            await ctx.send(f"No timers running for `{ctx.author}`.")

# --- Info Commands --- #

    @commands.command()
    async def info(self, ctx, group=None, idol=None):
        """
        returns info about the groups added to the bot;
        or the group specified, or the idol specified.
        Example: .info
        Example: .info <group>
        Example: .info <group> <idol>
        """
        dicto = gfys_dict["groups"]
        if group is None:
            await ctx.send(f"Groups: `{format_list(dicto.keys())}`")
        elif idol is not None and group is not None:
            idol = idol.lower()
            group = group.lower()
            if group not in gfys_dict["groups"]:
                await ctx.send(f"No group called {group}!")
            if idol in dicto[group]:
                idol_list = dicto[group][idol]
                is_tagged = []
                for tags in gfys_dict["tags"]:
                    i = 0
                    for element in gfys_dict["tags"][tags]:
                        if element in idol_list:
                            i += 1
                    if i > 0:
                        is_tagged.append(f"{tags}: {i}")
                if len(is_tagged) > 0:
                    is_tagged.sort()
                    a = idol.title()
                    b = str(len(idol_list))
                    c = format_list(is_tagged)
                    d = hide_links(idol_list[-3:])
                    s = (f'`{a}` has `{b}` link(s)! Tags: `{c}`. \n'
                         f'The last 3 links added: <{d}>')
                    await ctx.send(s)
                else:
                    a = idol.title()
                    b = str(len(idol_list))
                    c = hide_links(idol_list[-3:])
                    s = (f'`{a}` has `{b}` link(s)! \n'
                         f'The last 3 links added: <{c}>')
                    await ctx.send(s)
            else:
                await ctx.send(
                    f"Nothing for `{idol.title()}` in the group `{group}`.")
        elif group is not None:
            group = group.lower()
            if group in dicto:
                message = []
                for member in dicto[group]:
                    memb_list = dicto[group][member]
                    memb = f"{member}: {len(memb_list)}"
                    message.append(memb)
                await ctx.send(
                    f"`{group}`: `{format_list(message)}`.")
            else:
                await ctx.send(f"No group named `{group}`!")
        else:
            await ctx.send("Something went wrong!")

    @commands.command()
    async def totallinks(self, ctx):
        group_count = len(gfys_dict["groups"])
        member_count = sum([len(x) for x in gfys_dict["groups"].values()])
        member_list = [y.values() for y in gfys_dict["groups"].values()]
        flat_member_list = [g for c in member_list for g in c]
        count = sum([len(x) for x in flat_member_list])
        await ctx.send(f"There are currently `{count}` links of "
                       f"`{member_count}` members belonging to "
                       f"`{group_count}` groups!")

    @commands.command(aliases=['list'])
    async def listlinks(self, ctx, group, idol=None):
        """
        Returns a list of all links that belong to a specified group, or idol
        This command can be envoked with .listlinks OR .list
        Examples:
        .list <group>
        .list <group> <idol>
        .list redvelvet
        .list redvelvet joy
        """
        dicto = gfys_dict["groups"]
        if not idol:
            # this part is broken somewhere
            group = group.lower()
            if group in dicto:
                o = f'{group} \n'
                msg = [o]
                for m in dicto[group]:
                    s = (f"{m}: \n"
                         f"<{newline(dicto[group][m])}>")
                    print(f"s string: {s}")
                    msg.append(s)
                sen = '\n'.join(msg)
                if len(sen) > 1500:
                    await ctx.message.add_reaction(emoji='✉')
                    send = []
                    n = 1500
                    while sen:
                        if len(sen) > n:
                            send.append(sen[:n])
                            sen = sen[n:]
                        else:
                            send.append(sen)
                            break
                    for elem in send:
                        await ctx.message.author.send(elem)
                else:
                    await ctx.message.add_reaction(emoji='✉')
                    await ctx.message.author.send(sen)
            else:
                des = f"No group named {group}!"
                er = discord.Embed(title='Error!',
                                   description=des,
                                   color=discord.Color.red())
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send(embed=er)
        elif idol:
            group = group.lower()
            idol = idol.lower()
            if group in dicto:
                if idol in dicto[group]:
                    s = (f"All links for: `{idol}`: \n"
                         f"<{newline(dicto[group][idol])}>")
                    if len(s) > 1500:
                        await ctx.message.add_reaction(emoji='✉')
                        send = []
                        n = 1500
                        # need to pick to cut so that links are not sent like;
                        # <https://gfycat.com/blushing
                        # shadyhoiho-jennie>
                        # due to the cutting at 1500 intervals
                        while s:
                            if len(s) > n:
                                send.append(s[:n])
                                s = s[n:]
                            else:
                                send.append(s)
                                break
                        for elem in send:
                            await ctx.message.author.send(elem)
                    else:
                        await ctx.message.add_reaction(emoji='✉')
                        await ctx.message.author.send(s)
                else:
                    des = f"No `{idol}` in `{group}`!"
                    er = discord.Embed(title='Error!',
                                       description=des,
                                       color=discord.Color.red())
                    await ctx.message.add_reaction(emoji='✉')
                    await ctx.message.author.send(embed=er)
            else:
                des = f"No group named `{group}`!"
                er = discord.Embed(title='Error!',
                                   description=des,
                                   color=discord.Color.red())
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send(embed=er)
        else:
            des = "Invalid arguments! Try again or try `.help list`"
            er = discord.Embed(title='Error!',
                               description=des,
                               color=discord.Color.red())
            await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send(embed=er)

# --- Auditing --- #

    async def audit_channel(self, group, idol, link, author):
        """To keep gfycat links safe and within rules of what can be added
        main channel is in the official discord, other auditing channels can
        be made by mods, author names will be omitted in those."""
        main_audcha = self.disclient.get_channel(auditing_dict["main_channel"])
        s = f'`{author}` added:\n`{group}`, `{idol}`: {link}'
        await main_audcha.send(s)
        if auditing_dict["auditing_channels"]:
            for chan in auditing_dict["auditing_channels"]:
                channel = self.disclient.get_channel(chan)
                fstr = f'Added: `{group}`, `{idol}`: {link}'
                try:
                    await channel.send(fstr)
                except AttributeError:
                    print("channel deleted")
                    contri_dict["auditing_channels"].remove(chan)


# --- End of Class --- #


def format_list(array):
    formatted = '`, `'.join(array)
    return formatted


def hide_links(array):
    hidden = '> <'.join(array)
    return hidden


def newline(array):
    newliner = '>\n<'.join(array)
    return newliner


def setup(disclient):
    disclient.add_cog(Fun(disclient))
