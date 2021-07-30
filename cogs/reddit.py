import discord
import asyncpraw
from discord.ext import commands
import asyncio
from data import get_all_subreddits, get_channels_with_sub, remove_channel_from_subreddit, add_reddit_channel, \
    add_reddit, get_subreddit_id, find_channel, add_channel
from data import apis_dict
from embeds import success_embed, error_embed


def get_and_format_subs_list():
    return [x[0] for x in get_all_subreddits()]


def get_and_format_channels_with_sub(sub_name):
    return [x[0] for x in get_channels_with_sub(sub_name)]


class Reddits(commands.Cog):
    """Get new posts from your favourite Subreddits
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        # possibly save recent posts to file to avoid reposts on restart
        self.recent_posts = {}
        self.disclient.loop.create_task(self.post_new())

    async def post_new(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            reddit = asyncpraw.Reddit(client_id=apis_dict["reddit_id"],
                                      client_secret=apis_dict["reddit_secret"],
                                      user_agent="idk what this is")
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
                        if channels not in self.recent_posts[subs]:
                            self.recent_posts[subs].update({channels: []})
                        lp = self.recent_posts[subs][channels]
                        channel = self.disclient.get_channel(int(channels))
                        if perm in lp:
                            continue
                        else:
                            soy = "https://reddit.com"
                            if len(lp) > 10:
                                lp.pop(0)
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
                            lp.append(perm)
            await reddit.close()
            await asyncio.sleep(600)

    @commands.command()
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
        found = find_channel(channel)
        if not found:
            add_channel(channel)
            found = find_channel(channel)
        added = add_reddit_channel(found[0], subreddit_id[0])
        if added:
            msg = f"Added {subreddit} to this channel!"
            await ctx.send(embed=success_embed(msg))
        else:
            msg = f"Already added {subreddit} to this channel!"
            await ctx.send(embed=error_embed(msg))


def setup(disclient):
    disclient.add_cog(Reddits(disclient))
