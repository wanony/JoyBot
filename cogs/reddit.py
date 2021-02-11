import discord
import json
import asyncpraw
from discord.ext import commands
import asyncio
from data import direc_dict
from data import apis_dict
from data import reddit_dict


class Reddits(commands.Cog):
    """Get new posts from your favourite Subreddits
    """
    def __init__(self, disclient):
        self.disclient = disclient
        self.disclient.loop.create_task(self.post_new())
        self.disclient.loop.create_task(self.write_reddit())
        self.reddit = asyncpraw.Reddit(client_id=apis_dict["reddit_id"],
                                       client_secret=apis_dict["reddit_secret"],
                                       user_agent="idk what this is")

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
            try:
                for subs in reddit_dict:
                    sub = await self.reddit.subreddit(subs)
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
                        for channels in reddit_dict[subs]["channels"]:
                            lp = reddit_dict[subs]["last_post"]
                            channel = self.disclient.get_channel(int(channels))
                            if perm in lp:
                                pass
                            else:
                                soy = "https://reddit.com"
                                lp.append(perm)
                                if len(lp) > 10:
                                    del lp[0]
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
            except Exception as e:
                print(e)
            await asyncio.sleep(600)
        # print("calling reddit")

    @commands.command()
    async def unfollow_subreddit(self, ctx, subreddit):
        """Unfollow a previously followed subreddit"""
        channel = ctx.channel.id
        subreddit = subreddit.lower()
        if subreddit in reddit_dict:
            if channel in reddit_dict[subreddit]["channels"]:
                reddit_dict[subreddit]["channels"].remove(channel)
                if not reddit_dict[subreddit]["channels"]:
                    del reddit_dict[subreddit]
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
            msg = f"{subreddit} is not followed in this channel"
            embed = discord.Embed(title="Error",
                                  description=msg,
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command()
    async def follow_subreddit(self, ctx, subreddit):
        """Add a subreddit to follow in this server!
        The channel this command is invoked in will be used
        to post the new submission to the sub"""
        channel = ctx.channel.id
        subreddit = subreddit.lower()
        if subreddit in reddit_dict:
            if channel in reddit_dict[subreddit]["channels"]:
                msg = f"Already added {subreddit} to this channel!"
                embed = discord.Embed(title="Error",
                                      description=msg,
                                      color=discord.Color.red())
                await ctx.send(embed=embed)
            else:
                reddit_dict[subreddit]["channels"].append(channel)
                msg = f"Added {subreddit} to this channel!"
                embed = discord.Embed(title="Success",
                                      description=msg,
                                      color=discord.Color.green())
                await ctx.send(embed=embed)
        else:
            updater = {subreddit: {"channels": [channel], "last_post": []}}
            reddit_dict.update(updater)
            msg = f"Added {subreddit} to this channel!"
            embed = discord.Embed(title="Success",
                                  description=msg,
                                  color=discord.Color.green())
            await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Reddits(disclient))
