import discord
import json
import praw
from discord.ext import commands
import asyncio
from data import direc_dict
from data import apis_dict
from data import reddit_dict

reddit = praw.Reddit(client_id=apis_dict["reddit_id"],
                     client_secret=apis_dict["reddit_secret"],
                     user_agent="idk what this is")


class Reddits(commands.Cog):
    """Get new posts from your favourite Subreddits
    """
    def __init__(self, disclient):
        self.disclient = disclient
        self.disclient.loop.create_task(self.post_new())
        self.disclient.loop.create_task(self.write_reddit())

    @commands.Cog.listener()
    async def write_reddit(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            with open(direc_dict["reddit"], 'w') as red:
                json.dump(reddit_dict, red, indent=4)
            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def post_new(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            for channels in reddit_dict:
                for subs in reddit_dict[channels]:
                    channel = self.disclient.get_channel(int(channels))
                    chanid = str(channel.id)
                    sub = reddit.subreddit(subs).new(limit=3)
                    for subm in sub:
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
                        lp = reddit_dict[chanid][subs]["last_post"]
                        if perm in lp:
                            pass
                        else:
                            soy = "https://reddit.com"
                            lp.append(perm)
                            if len(lp) > 5:
                                del lp[0]
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
                                        print("Channel deleted")
                                elif url.startswith(gifs):
                                    embed.add_field(name="Post Permalink",
                                                    value=val)
                                    try:
                                        await channel.send(embed=embed)
                                        await channel.send(url)
                                    except AttributeError:
                                        print("Channel deleted")
                                else:
                                    val = f"{soy}{perm}"
                                    embed.add_field(name="Post Permalink",
                                                    value=val)
                                    try:
                                        await channel.send(embed=embed)
                                        await channel.send(url)
                                    except AttributeError:
                                        print("Channel deleted")
                            else:
                                val = f"{soy}{perm}"
                                embed.add_field(name="Post Permalink",
                                                value=val)
                                try:
                                    await channel.send(embed=embed)
                                except AttributeError:
                                    print("Channel deleted")
            await asyncio.sleep(210)
            # print("calling reddit")

    @commands.command()
    async def unfollow_subreddit(self, ctx, subreddit):
        """Unfollow a previously followed subreddit"""
        channel = str(ctx.channel.id)
        subreddit = subreddit.lower()
        if channel in reddit_dict:
            if subreddit in reddit_dict[channel]:
                del reddit_dict[channel][subreddit]
                if not reddit_dict[channel]:
                    del reddit_dict[channel]
                msg = f"Unfollowed {subreddit} in this channel!"
                embed = discord.Embed(title="Success",
                                      description=msg,
                                      color=discord.Color.green())
                await ctx.send(embed=embed)
            else:
                msg = f"{subreddit} is not followed in this channel"
                embed = discord.Embed(title="Error",
                                      description=msg,
                                      color=discord.Color.red())
                await ctx.send(embed=embed)
        else:
            msg = "No subreddits are followed in this channel"
            embed = discord.Embed(title="Error",
                                  description=msg,
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command()
    async def follow_subreddit(self, ctx, subreddit):
        """Add a subreddit to follow in this server!
        The channel this command is invoked in will be used
        to post the new submission to the sub"""
        channel = str(ctx.channel.id)
        subreddit = subreddit.lower()
        if channel in reddit_dict:
            if subreddit in reddit_dict[channel]:
                msg = f"Already added {subreddit} to this channel!"
                embed = discord.Embed(title="Error",
                                      description=msg,
                                      color=discord.Color.red())
                await ctx.send(embed=embed)
            else:
                updater = {subreddit: {"last_post": []}}
                reddit_dict[channel].update(updater)
                msg = f"Added {subreddit} to this channel!"
                embed = discord.Embed(title="Success",
                                      description=msg,
                                      color=discord.Color.green())
                await ctx.send(embed=embed)
        else:
            updater = {channel: {subreddit: {"last_post": []}}}
            reddit_dict.update(updater)
            msg = f"Added {subreddit} to this channel!"
            embed = discord.Embed(title="Success",
                                  description=msg,
                                  color=discord.Color.green())
            await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Reddits(disclient))
