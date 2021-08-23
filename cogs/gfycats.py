import os

from discord.ext import commands
import urllib.request
import datetime

from cogs.mods import is_mod
from data import PfyClient

from embeds import error_embed


class Gfycat(commands.Cog):
    def __init__(self, disclient):
        self.disclient = disclient
        self.pfy = PfyClient(self.disclient)

    @commands.command(name='uploadgfy')
    @commands.guild_only()
    @is_mod()
    async def _upload_gfy(self, ctx, url=None):
        """Upload a video to gfycat!
        Either upload a discord attachment, or provide a valid video url!"""
        async with ctx.channel.typing():
            msg = await ctx.send('Processing...')
            # set unique name for file to save to
            filename = f'gfy_video{datetime.datetime.now().timestamp()}.webm'
            # if nothing provided then return error
            if not ctx.message.attachments and url is None:
                await msg.edit(embed=error_embed('Make sure to attach a video or provide a valid video URL!'))
                return
            # if video is from a url, use urllib to download
            elif url is not None and 'http' in url:
                try:
                    urllib.request.urlretrieve(url, filename)
                except Exception as e:
                    print(e)
                    await msg.edit(embed=error_embed('Could not retrieve the video from that URL!'))
                    return
            elif ctx.message.attachments:
                # only save first video
                await ctx.message.attachments[0].save(filename)
            url = await self.pfy.upload_video(filename)
            await msg.edit(content=f'Successfully uploaded!\n{url}')
        os.remove(filename)


def setup(disclient):
    disclient.add_cog(Gfycat(disclient))
