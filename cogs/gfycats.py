import os

import discord

from bot import executor
from nextcord.ext import commands
import urllib.request
import datetime
from data import apis_dict, default_prefix
import pfycat
import concurrent.futures
from pathlib import Path

from embeds import error_embed


def handle_upload_finish(interaction, future: concurrent.futures.Future, author, disclient, filename):
    if not future.cancelled():
        disclient.loop.create_task(finish_upload(interaction, filename, future.result(), author))
    else:
        disclient.loop.create_task(interaction.response.send_message(embed=error_embed('Failed to upload!')))


async def finish_upload(interaction, path, url, author):
    await interaction.response.send_message(content=f'Successfully uploaded! {author.mention}\n{url}')
    os.remove(path)


class PfyClient:
    def __init__(self, disclient, api_key, api_sec):
        self.api_key = api_key
        self.api_sec = api_sec
        self.disclient = disclient
        self.client = pfycat.Client(self.api_key, self.api_sec)

    def upload_video(self, video_file_path):
        """Returns gfycat link of video uploaded"""
        upload = self.client.upload(video_file_path)
        gfy_url = f"https://gfycat.com/{upload['gfyname']}"
        return gfy_url

    def upload_multiple_videos(self, video_file_paths):
        """Returns a list of tuples, containing link and filepath"""
        return_list = []
        print(video_file_paths)
        if video_file_paths:
            for path in video_file_paths:
                if path.endswith('.webm'):
                    return_list.append((self.upload_video(path), path))
                else:
                    return_list.append((path, None))
        return return_list


class Uploading(commands.Cog):
    """Upload videos to Gfycat through discord!"""

    def __init__(self, disclient, api_key, api_sec):
        self.disclient = disclient
        self.pfy = PfyClient(self.disclient, api_key, api_sec)

    @discord.slash_command(
        name="uploadgfy",
        description="upload a video to gfycat"
    )
    @commands.guild_only()  # force guild to attempt to avoid spam
    # @is_mod()
    async def _upload_gfy(self, interaction: discord.Interaction, url=None):
        """Upload a video to gfycat!
        Either upload a discord attachment, or provide a valid video url!"""
        # set unique name for file to save to
        filename = Path(f'gfy_video{datetime.datetime.now().timestamp()}.webm').resolve()
        # if nothing provided then return error
        if not interaction.message.attachments and url is None:
            await interaction.response.send_message(
                embed=error_embed('Make sure to attach a video or provide a valid video URL!'))
            return

        # if video is from a url, use urllib to download
        elif url is not None and 'http' in url:
            try:
                urllib.request.urlretrieve(url, filename)
            except Exception as e:
                print(e)
                await interaction.response.send_message(
                    embed=error_embed('Could not retrieve the video from that URL!'))
                return

        elif interaction.message.attachments:
            # video download
            await interaction.message.attachments[0].save(filename)
            # concurrent future XD
            x = executor.submit(self.pfy.upload_video, filename)
            # pep e731 is for uncool kids :sunglasses: :thumbsup:

            def func(future):
                handle_upload_finish(interaction, future, interaction.user, self.disclient, filename)

            x.add_done_callback(func)


def setup(disclient):
    try:
        api_key = apis_dict['gfy_client_id']
        api_sec = apis_dict['gfy_client_secret']
        if api_key.strip() == "" or api_sec.strip() == "":
            print(f"Api key or secret missing, skipping loading cog gfycat")
            return
        disclient.add_cog(Uploading(disclient, api_key, api_sec))
    except Exception as e:
        print(f"gfycats cog could not be loaded")
        print(e)
