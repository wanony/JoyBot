import codecs
import datetime
import concurrent.futures
import json
import os
import asyncio
from bot import executor
from pathlib import Path

import pyshorteners
from cogs.gfycats import PfyClient

import discord
import urllib.request
from discord.utils import escape_markdown
from instagram_private_api import Client, ClientLoginRequiredError, ClientCookieExpiredError, \
    ClientChallengeRequiredError
from discord.ext import commands
from data import apis_dict, insta_settings_file, get_insta_users_to_check, get_channels_following_insta_user, \
    get_all_instas_followed_in_guild, follow_insta_user_db, unfollow_insta_user_db, add_insta_user_to_db, \
    add_channel, set_min_timestamp, get_min_timestamp

# https://github.com/ping/instagram_private_api/blob/master/examples/savesettings_logincallback.py
from embeds import error_embed, success_embed

INSTA_COLOUR = 0xDD2A7B


def handle_upload_finish(future: concurrent.futures.Future, disclient: discord.Client,
                         embed, channels: list):
    if not future.cancelled():
        disclient.loop.create_task(finish_upload(embed, channels, disclient, future.result()))


async def finish_upload(embed, channels, disclient, url_to_path_pairs):
    for channel in channels:
        chan = disclient.get_channel(channel)
        await chan.send(embed=embed)
        links = url_to_path_pairs  # list of urls
        # i = 0
        # while i < (len(links)):
        #     await chan.send('\n'.join(link for link, _ in links[i:i+4]))
        #     i += 4
        for link, _ in links:
            await chan.send(link)
    for p in [path for _, path in url_to_path_pairs if path]:
        os.remove(p)


async def handle_message_one_image(message, disclient, channels):
    embed = message
    for channel in channels:
        await disclient.get_channel(channel).send(embed=embed)


def handle_carousel(embed, filename_or_links, gfy, disclient, channels):

    x = executor.submit(gfy.upload_multiple_videos, filename_or_links)

    def func(future):
        # pass all the info we need to send the messages here
        handle_upload_finish(future, disclient, embed, channels)

    x.add_done_callback(func)


def get_highest_resolution_image_for_embed(post):
    image_url = discord.Embed.Empty
    for images in post['image_versions2']['candidates']:
        if post['original_width'] == images['width']:  # grab url with highest resolution
            image_url = images['url']
    return image_url


def download_url(url, prefix='file'):
    if not url:
        raise ValueError('url is none')
    filename = Path(f'{prefix}{datetime.datetime.now().timestamp()}.webm').resolve().as_posix()
    try:
        filename = urllib.request.urlretrieve(url, filename)[0]
    except Exception as e:
        raise e
    return filename


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('Written instagram settings file.')


class InstaClient:
    def __init__(self, disclient, api_key, api_sec):
        self.device_id = None
        self.disclient = disclient
        self.gfy = PfyClient(self.disclient, api_key, api_sec)
        try:
            if os.path.isfile(insta_settings_file):
                with open(insta_settings_file) as w:
                    cached_settings = json.load(w, object_hook=from_json)
                self.api = Client(apis_dict["instagram_key"],
                                  apis_dict["instagram_secret"],
                                  settings=cached_settings,
                                  on_login=print("Instagram Client successfully started!"))
            else:
                self.api = Client(apis_dict["instagram_key"],
                                  apis_dict["instagram_secret"],
                                  on_login=lambda x: onlogin_callback(x, insta_settings_file))
        except (ClientLoginRequiredError, ClientCookieExpiredError) as e:
            print(f'Insta login expired: {e}')
            self.api = Client(apis_dict["instagram_key"],
                              apis_dict["instagram_secret"],
                              device_id=self.device_id,
                              on_login=lambda x: onlogin_callback(x, insta_settings_file))
        except ClientChallengeRequiredError:
            msg = 'Client Challenge Required Error, please log in manually to Instagram Captcha required.'
            channel = self.disclient.get_channel(apis_dict['error_channel'])
            owner = self.disclient.get_user(107215130785243136)
            self.disclient.loop.create_task(channel.send(f'{owner.mention} {msg}'))
        self.cookie_expiry = self.api.cookie_jar.auth_expires
        print(f"Cookie Expiry: {datetime.datetime.fromtimestamp(self.cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')}")

    def get_user(self, user_name):
        user_info = self.api.username_info(user_name)
        return user_info

    def get_user_name(self, user_id):
        user_info = self.api.user_info(user_id)
        user_name = user_info['user']['username']
        return user_name

    async def get_user_feed(self, user_id):
        min_timestamp = get_min_timestamp(user_id)
        # grab all results that are posted after the minimum timestamp
        result_list = self.api.user_feed(user_id, min_timestamp=min_timestamp)
        if result_list and result_list['items']:
            set_min_timestamp(user_id, result_list['items'][0]['taken_at'])
            return result_list['items']
        return []

    async def format_user_feed_result(self, post_list, channels):
        for post in post_list:
            username = f"@{escape_markdown(post['user']['username'])}"
            try:
                text = post["caption"]["text"]
            except TypeError:
                text = ''
            name = post['user']['full_name']
            profile_pic_url = post['user']['profile_pic_url']
            link = f"https://www.instagram.com/p/{post['code']}/"
            embed = discord.Embed(title=f'{name} ({username})',
                                  description=f'{text}\n{link}',
                                  color=INSTA_COLOUR)
            embed.set_footer(text=f"Posted to Instagram by {post['user']['username']}",
                             icon_url=profile_pic_url)
            # check if post is video, '2' or image, '1', else is for carousel posts with multiple images or videos
            if post['media_type'] == 1:
                # one picture
                embed.set_image(url=get_highest_resolution_image_for_embed(post))
                # messages.append((embed, post_id))  # append embed of type discord.Embed
                await handle_message_one_image(embed, self.disclient, channels)
            elif post['media_type'] == 2:
                # one video
                video_url = post['video_versions'][0]['url']
                filename = download_url(video_url, prefix='instavid')
                # messages.append((embed, post_id, filename))  # append tuple with embed and filename
                handle_carousel(embed, [filename], self.gfy, self.disclient, channels)
            else:
                # multiple photos or videos
                links = []  # hold the links for each post
                # short = pyshorteners.Shortener()
                for item in post['carousel_media']:
                    if item['media_type'] == 1:
                        for images in item['image_versions2']['candidates']:
                            if item['original_width'] == images['width']:
                                # links.append(short.tinyurl.short(images['url']))  # simply append the image urls
                                links.append(images['url'])  # simply append the image urls
                    else:
                        filename = download_url(item['video_versions'][0]['url'], 'instavid')
                        links.append(filename)
                # messages.append((embed, post_id, links, 'carousel'))
                handle_carousel(embed, links, self.gfy, self.disclient, channels)


class Instagram(commands.Cog):
    """Get new posts from your favourite Instagram accounts!
    """

    def __init__(self, disclient, api_key, api_sec):
        """Initialise client."""
        self.disclient = disclient
        self.insta = InstaClient(self.disclient, api_key, api_sec)
        self.disclient.loop.create_task(self.check_for_new_posts())

    async def check_for_new_posts(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            try:
                print('checking instagram for posts!')
                # TODO rewrite get_insta_users_to_check SQL to only grab followed with join on instagram_channels
                insta_users = get_insta_users_to_check()
                if not insta_users:
                    continue
                for user in insta_users:
                    following_user = get_channels_following_insta_user(user)
                    if not following_user:
                        continue
                    try:
                        posts = await self.insta.get_user_feed(user)
                    except Exception as e:
                        print(f'No new posts, or user is private. {e}')
                        await asyncio.sleep(1800)
                        continue
                    await self.insta.format_user_feed_result(posts,
                                                             following_user)
                    await asyncio.sleep(1800 // len(insta_users))
            except Exception as e:
                print(f'Instagram exception: {e}')
            finally:
                await asyncio.sleep(1800)

    @commands.command(aliases=['followinsta', 'instafollow', 'insta_follow', 'follow_instagram', 'instagram_follow'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def follow_insta(self, ctx, user_name):
        """Follows an Instagram user in this channel.
        Example: `.follow_insta <username or link>`"""
        if 'instagram.com' in user_name:
            user_name = user_name.split('/')[-1]
        user = self.insta.get_user(user_name)
        try:
            if user['is_private']:
                await ctx.send(embed=error_embed('This user is private, and cannot be followed!'))
                return

        except Exception as e:
            print(e)
        user_id = user['user']['pk']
        if not user_id:
            await ctx.send(embed=error_embed(f'No instagram user found called {escape_markdown(user_name)}!'))
            return

        add_insta_user_to_db(user_id)
        add_channel(ctx.channel.id)
        if not follow_insta_user_db(user_id, ctx.channel.id):
            await ctx.send(embed=error_embed(f'{escape_markdown(user_name)} is already followed in this channel!'))
            return

        name = user['user']['full_name']
        link = f"https://www.instagram.com/{user['user']['username']}"
        embed = discord.Embed(title=f'Successfully followed {name}',
                              description=f'This channel will now receive updates when {name} posts updates at {link}',
                              color=INSTA_COLOUR)
        embed.set_thumbnail(url=user['user']['profile_pic_url'])
        await ctx.send(embed=embed)

    @commands.command(aliases=[
        'unfollowinsta', 'instaunfollow', 'insta_unfollow', 'unfollow_instagram', 'instagram_unfollow'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unfollow_insta(self, ctx, user_name):
        """Unfollows an Instagram user in this channel.
        Example: `.unfollow_insta <username or link>`"""
        if 'instagram.com' in user_name:
            user_name = user_name.split('/')[-1]
        user = self.insta.get_user(user_name)
        user_id = user['user']['pk']
        if not user_id:
            await ctx.send(embed=error_embed(f'No instagram user found called {escape_markdown(user_name)}!'))
            return

        if unfollow_insta_user_db(user_id, ctx.channel.id):
            await ctx.send(embed=success_embed(f'Unfollowed {escape_markdown(user_name)}!'))
        else:
            await ctx.send(embed=error_embed(f'Failed to unfollow {escape_markdown(user_name)}!'))

    @commands.command()
    @commands.guild_only()
    async def instas(self, ctx):
        """Returns a list of all instagram users followed in this server!"""
        guild = ctx.guild
        chans = get_all_instas_followed_in_guild()
        chan_dict = {}
        for pair in chans:
            if pair[0] not in chan_dict:
                chan_dict.update({pair[0]: [pair[-1]]})
            else:
                chan_dict[pair[0]].append(pair[-1])
        msg = ''
        for channel in guild.channels:
            if channel.id in chan_dict:
                for insta in chan_dict[channel.id]:
                    insta = self.insta.get_user_name(insta)
                    spacing = 39 - len(channel.name + insta)
                    chan_str = f"`#{channel.name}{' ' * spacing}{insta}`\n"
                    msg = msg + chan_str
        if msg == '':
            await ctx.send(embed=error_embed('No instagram users followed in this server!'))
        else:
            add_to_start = f"`Channel Name{' ' * 14}Instagram User`\n"
            msg = add_to_start + msg
            embed = discord.Embed(title=f'Instagram Users Followed in {guild.name}!',
                                  description=msg,
                                  color=INSTA_COLOUR)
            await ctx.send(embed=embed)

    # @commands.command()
    # async def find_user_by_id(self, ctx, insta_id):
    #     user = self.insta.get_user_name(insta_id)
    #     await ctx.send(user)


def setup(disclient):
    try:
        api_key = apis_dict['gfy_client_id']
        api_sec = apis_dict['gfy_client_secret']
        if api_key.strip() == "" or api_sec.strip() == "":
            print(f"Api key or secret missing, skipping loading cog gfycat")
            return
        disclient.add_cog(Instagram(disclient, api_key, api_sec))
    except Exception as e:
        print(f"gfycats cog could not be loaded")
        print(e)