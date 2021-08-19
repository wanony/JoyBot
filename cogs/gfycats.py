import discord
from discord.ext import commands
from data import apis_dict
import asyncio
import pfycat


class PfyClient:
    def __init__(self):
        self.api_key = apis_dict['gfy_client_id']
        self.api_sec = apis_dict['gfy_client_secret']
        self.client = pfycat.Client(self.api_key, self.api_sec)

    async def upload_video(self, video_file_path):
        # wait until video is downloaded, lets try 10 seconds
        await asyncio.sleep(10)
        upload = self.client.upload(video_file_path)
        gfy_url = f"https://gfycat.com/{upload['gfyname']}"
        return gfy_url


class Gfycat(commands.Cog):
    def __init__(self, disclient):
        self.disclient = disclient
        self.client = PfyClient()

    @commands.command(name='uploadgfy')
    async def _upload_gfy(self, attachments):
        """Upload a video to gfycat by uploading it in a discord attachment!"""
        pass


def setup(disclient):
    disclient.add_cog(Gfycat(disclient))
