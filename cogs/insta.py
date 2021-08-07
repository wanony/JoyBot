import codecs
import datetime
import json
import os
import asyncio

import discord
from discord.utils import escape_markdown
from instagram_private_api import Client, ClientLoginRequiredError, ClientCookieExpiredError
from instagram_private_api_extensions.pagination import page
from discord.ext import commands
from data import apis_dict, insta_settings_file, get_insta_users_to_check, get_channels_following_insta_user, \
    cache_dict, get_all_instas_followed_in_guild, follow_insta_user_db, unfollow_insta_user_db, add_insta_user_to_db, \
    add_channel

# following three functions shamelessly stolen from
# https://github.com/ping/instagram_private_api/blob/master/examples/savesettings_logincallback.py
from embeds import error_embed, success_embed

insta_colour = 0xDD2A7B


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


def format_user_feed_result(result):
    # check if post is video, '2' or image, '1', else is for carousel posts
    if '_' in result['user']['username']:
        username = f"@{escape_markdown(result['user']['username'])}"
    else:
        username = f"@{result['user']['username']}"
    text = result["caption"]["text"]
    name = result['user']['full_name']
    profile_pic_url = result['user']['profile_pic_url']
    link = f"https://www.instagram.com/p/{result['code']}/"
    image_url = None
    if result['media_type'] == 1:
        for images in result['image_versions2']['candidates']:
            if result['original_width'] == images['width']:
                image_url = images['url']
    elif result['media_type'] == 2:
        image_url = result['image_versions2']['candidates'][0]['url']
    else:
        if result['carousel_media'][0]['media_type'] == 1:
            for images in result['carousel_media'][0]['image_versions2']['candidates']:
                if result['carousel_media'][0]['original_width'] == images['width']:
                    image_url = images['url']
        else:
            image_url = result['carousel_media'][0]['image_versions2']['candidates'][0]['url']
    embed = discord.Embed(title=f'{name} ({username})',
                          description=f"{text}\n{link}",
                          color=insta_colour)
    if image_url:
        embed.set_image(url=image_url)
    embed.set_footer(text=f"Posted to instagram by {result['user']['username']}",
                     icon_url=profile_pic_url)
    return embed


class InstaClient:
    def __init__(self):
        self.device_id = None
        self.min_timestamps = cache_dict["instagram"]["min_timestamps"]
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
        self.cookie_expiry = self.api.cookie_jar.auth_expires
        print(f"Cookie Expiry: {datetime.datetime.fromtimestamp(self.cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')}")

    def get_user_id(self, user_name):
        user_info = self.api.username_info(user_name)
        user_id = user_info['user']['pk']
        return user_id

    def get_user_name(self, user_id):
        user_info = self.api.user_info(user_id)
        user_name = user_info['user']['username']
        return user_name

    async def get_user_feed(self, user_id):
        result_list = []
        user_str = str(user_id)
        if user_str in self.min_timestamps:
            min_timestamp = self.min_timestamps[user_str]
        else:
            self.min_timestamps.update({user_str: 1})
            min_timestamp = 1
        # if possible it would be nice to find a way to just get the one result
        for results in page(self.api.user_feed,
                            args={'user_id': str(user_id),
                                  'min_timestamp': min_timestamp},
                            wait=None):
            if results.get('items'):
                # instead of adding them all to a list... seems dumb
                result_list.extend(results['items'])
                self.min_timestamps[user_str] = result_list[0]['device_timestamp']
                return result_list[0]
        return

    async def get_feed_no_page(self, user_id):
        results = self.api.user_feed(user_id)
        return format_user_feed_result(results)


class Instagram(commands.Cog):
    """Get new posts from your favourite Instagram accounts!
    """

    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        self.sent_posts = cache_dict["instagram"]["sent_posts"]
        self.insta = InstaClient()
        self.disclient.loop.create_task(self.check_for_new_posts())

    async def check_for_new_posts(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            insta_users = get_insta_users_to_check()
            if not insta_users:
                await asyncio.sleep(600)
                continue
            for user in insta_users:
                user_str = str(user)
                if user_str not in self.sent_posts:
                    self.sent_posts.update({user_str: {}})
                info = await self.insta.get_user_feed(user)
                following_user = get_channels_following_insta_user(user)
                if not following_user:
                    continue
                for channels in following_user:
                    chan_str = str(channels)
                    if chan_str not in self.sent_posts[user_str]:
                        self.sent_posts[user_str].update({chan_str: []})
                    if info['id'] not in self.sent_posts[user_str][chan_str]:
                        channel = self.disclient.get_channel(channels)
                        refined = format_user_feed_result(info)
                        await channel.send(embed=refined)
                        self.sent_posts[user_str][chan_str].append(info['id'])
                    if len(self.sent_posts[user_str][chan_str]) > 5:
                        self.sent_posts[user_str][chan_str].pop(0)
            await asyncio.sleep(600)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def follow_insta(self, ctx, user_name):
        """Follows an Instagram user in this channel.
        Example: `.follow_insta <username or link>`"""
        if 'instagram.com' in user_name:
            user_name = user_name.split('/')[-1]
        user_id = self.insta.get_user_id(user_name)
        if user_id:
            add_insta_user_to_db(user_id)
        channel_id = ctx.channel.id
        add_channel(channel_id)
        followed = follow_insta_user_db(user_id, channel_id)
        if followed:
            await ctx.send(embed=success_embed(f'Followed {user_name}!'))
        else:
            await ctx.send(embed=error_embed(f'Failed to follow {user_name}!'))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unfollow_insta(self, ctx, user_name):
        """Unfollows an Instagram user in this channel.
        Example: `.unfollow_insta <username or link>`"""
        if 'instagram.com' in user_name:
            user_name = user_name.split('/')[-1]
        user_id = self.insta.get_user_id(user_name)
        if not user_id:
            await ctx.send(embed=error_embed(f'No instagram user found called {user_name}!'))
        channel_id = ctx.channel.id
        unfollowed = unfollow_insta_user_db(user_id, channel_id)
        if unfollowed:
            await ctx.send(embed=success_embed(f'Unfollowed {user_name}!'))
        else:
            await ctx.send(embed=error_embed(f'Failed to unfollow {user_name}!'))

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
                                  color=discord.Color.blue())
            await ctx.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Instagram(disclient))
