import discord
import asyncpraw
from discord.ext import commands
import asyncio
from data import get_all_subreddits, get_channels_with_sub, remove_channel_from_subreddit, add_reddit_channel, \
    add_reddit, get_subreddit_id, find_channel, add_channel, get_all_reddit_channels_and_sub, cache_dict
from data import apis_dict
from embeds import success_embed, error_embed


def get_and_format_subs_list():
    return [x[0] for x in get_all_subreddits()]


def get_and_format_channels_with_sub(sub_name):
    return [x[0] for x in get_channels_with_sub(sub_name)]


def create_reddit_instance():
    reddit = asyncpraw.Reddit(client_id=apis_dict["reddit_id"],
                              client_secret=apis_dict["reddit_secret"],
                              user_agent="idk what this is")
    return reddit


class Reddit(commands.Cog):
    """Get new posts from your favourite Subreddits!
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        self.recent_posts = cache_dict["reddit"]["recent_posts"]
        self.disclient.loop.create_task(self.post_new())

    async def post_new(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            reddit = create_reddit_instance()
            subs_list = get_and_format_subs_list()
            for subs in subs_list:
                channels_with_reddit = get_and_format_channels_with_sub(subs)
                if not channels_with_reddit:
                    continue
                # do as much processing before reddit call
                sub = await reddit.subreddit(subs)
                async for subm in sub.new(limit=5):
                    titl = subm.title
                    if "/r/" in subm.url:
                        url = ""
                    else:
                        url = subm.url
                    auth = subm.author
                    perm = subm.permalink
                    fts = (".JPG", ".jpg", ".JPEG",
                           ".jpeg", ".PNG", ".png")
                    gifs = (
                        "https://gfycat.com/",
                        "https://www.redgifs.com/",
                        "https://www.gifdeliverynetwork.com/"
                    )
                    for channels in channels_with_reddit:
                        if subs not in self.recent_posts:
                            self.recent_posts.update({subs: {}})
                        if str(channels) not in self.recent_posts[subs]:
                            self.recent_posts[subs].update({str(channels): []})
                        channel = self.disclient.get_channel(int(channels))
                        channels = str(channels)
                        if perm not in self.recent_posts[subs][channels]:
                            self.recent_posts[subs][channels].append(perm)
                            soy = "https://reddit.com"
                            if len(self.recent_posts[subs][channels]) > 10:
                                self.recent_posts[subs][channels].pop(0)
                            #  Embeds from this point
                            desc = f"Posted by {auth} in **/r/{subs}**"
                            clr = discord.Color.blurple()
                            embed = discord.Embed(title=titl,
                                                  description=desc,
                                                  color=clr)
                            if url:
                                val = f"{soy}{perm} \n**{url}**"
                                if url.endswith(fts) or "gallery" in url:
                                    embed.set_image(url=url)
                                    embed.add_field(name="Post Permalink",
                                                    value=val)
                                    try:
                                        await channel.send(embed=embed)
                                    except AttributeError:
                                        self.recent_posts[subs].pop(channels)
                                        print("Channel deleted")
                                elif url.startswith(gifs):
                                    embed.add_field(name="Post Permalink",
                                                    value=val)
                                    try:
                                        await channel.send(embed=embed)
                                        await channel.send(url)
                                    except AttributeError:
                                        self.recent_posts[subs].pop(channels)
                                        print("Channel deleted")
                                else:
                                    val = f"{soy}{perm}"
                                    embed.add_field(name="Post Permalink",
                                                    value=val)
                                    try:
                                        await channel.send(embed=embed)
                                        await channel.send(url)
                                    except AttributeError:
                                        self.recent_posts[subs].pop(channels)
                                        print("Channel deleted")
                            else:
                                val = f"{soy}{perm}"
                                embed.add_field(name="Post Permalink",
                                                value=val)
                                try:
                                    await channel.send(embed=embed)
                                except AttributeError:
                                    self.recent_posts[subs].pop(channels)
                                    print(f"Channel deleted")
            await reddit.close()
            await asyncio.sleep(600)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unfollow_subreddit(self, ctx, subreddit):
        """Unfollow a previously followed subreddit.
        Example: `.unfollow_subreddit <subreddit_name>`"""
        channel = ctx.channel.id
        subreddit = subreddit.lower()
        if '/r/' in subreddit:
            subreddit = subreddit.split('/r/')[-1]
        subreddit_id = get_subreddit_id(subreddit)
        if not subreddit_id:
            msg = f"{subreddit} is not found!"
            await ctx.send(embed=error_embed(msg))
            return
        found = find_channel(channel)
        if not found:
            msg = f"{subreddit} is not found!"
            await ctx.send(embed=error_embed(msg))
            return
        removed = remove_channel_from_subreddit(found[0], subreddit_id[0])
        if removed:
            msg = f"Unfollowed {subreddit} in this channel!"
            await ctx.send(embed=success_embed(msg))
        else:
            msg = f"{subreddit} is not followed in this channel"
            await ctx.send(embed=error_embed(msg))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def follow_subreddit(self, ctx, subreddit):
        """Add a subreddit to follow in this server!
        The channel this command is invoked in will be used
        to post the new submission to the sub.
        Example: `.follow_subreddit <subreddit_name>`"""
        channel = ctx.channel.id
        subreddit = subreddit.lower()
        if '/r/' in subreddit:
            subreddit = subreddit.split('/r/')[-1]
        subreddit_id = get_subreddit_id(subreddit)
        if not subreddit_id:
            add_reddit(subreddit)
            subreddit_id = get_subreddit_id(subreddit)
        add_channel(channel)
        found = find_channel(channel)
        added = add_reddit_channel(found[0], subreddit_id[0])
        if added:
            msg = f"Added {subreddit} to this channel!"
            await ctx.send(embed=success_embed(msg))
        else:
            msg = f"Already added {subreddit} to this channel!"
            await ctx.send(embed=error_embed(msg))

    @commands.command(aliases=['subreddits'])
    @commands.guild_only()
    async def reddits(self, ctx):
        """Returns a list of followed subreddits in this server."""
        guild = ctx.guild
        chans = get_all_reddit_channels_and_sub()
        chan_dict = {}
        for pair in chans:
            if pair[0] not in chan_dict:
                chan_dict.update({pair[0]: [pair[-1]]})
            else:
                chan_dict[pair[0]].append(pair[-1])
        msg = ''
        for channel in guild.channels:
            if channel.id in chan_dict:
                for reddit in chan_dict[channel.id]:
                    spacing = 39 - len(channel.name + reddit)
                    chan_str = f"`#{channel.name}{' ' * spacing}{reddit}`\n"
                    msg = msg + chan_str
        if msg == '':
            await ctx.send(embed=error_embed('No subreddits followed in this server!'))
        else:
            add_to_start = f"`Channel Name{' ' * 19}Subreddit`\n"
            msg = add_to_start + msg
            embed = discord.Embed(title=f'Subreddits Followed in {guild.name}!',
                                  description=msg,
                                  color=discord.Color.blurple())
            await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Reddit(disclient))
