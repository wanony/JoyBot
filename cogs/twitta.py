import asyncio
import json

import discord
import tweepy
from discord.ext import commands
from data import apis_dict, get_twitter_users_from_db, add_twitter_channel_to_db, remove_twitter_user_from_db, \
    add_twitter_to_db, add_channel, get_twitter_channels_following_user
from embeds import error_embed, success_embed


def authenticator():
    auth = tweepy.OAuthHandler(apis_dict["twitter_key"], apis_dict["twitter_secret"])
    auth.set_access_token(apis_dict["twitter_access_token"], apis_dict["twitter_access_secret"])
    return auth


def get_users_to_stream():
    users = get_twitter_users_from_db()
    return users


def twitter_image_link_formatting(link):
    if "twimg" in link:
        split_link = link.split("/")
        if "?" in split_link[-1]:
            splitt = split_link[-1].split("?")
            if "png" in splitt[-1]:
                newending = splitt[0] + "?format=png&name=orig"
            else:
                newending = splitt[0] + "?format=jpg&name=orig"
            link = "https://pbs.twimg.com/media/" + newending
        elif "." in split_link[-1]:
            splitt = split_link[-1].split(".")
            if "png" in splitt[-1]:
                newending = splitt[0] + "?format=png&name=orig"
            else:
                newending = splitt[0] + "?format=jpg&name=orig"
            link = "https://pbs.twimg.com/media/" + newending
    return link


class TwitterClient:
    def __init__(self):
        self.client = tweepy.API(authenticator())

    def get_twitter_user_id(self, user_name):
        user = self.client.get_user(user_name)
        user_id = user.id_str
        return user_id


class MyStreamListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__()
        self.new_tweet = None

    def on_data(self, raw_data):
        data = json.loads(raw_data)
        self.new_tweet = data

    def on_event(self, status):
        print(f"event: {status}")

    def on_connect(self):
        print('Twitter Stream Started!')

    def on_status(self, status):
        print(f"status: {status}")

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            return False
        return False


class Twitter(commands.Cog):
    """Get new posts from your favourite Subreddits
    """
    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        self.current_stream = tweepy.Stream(authenticator(), MyStreamListener())
        self.current_stream.filter(follow=get_users_to_stream(), is_async=True)
        self.client = TwitterClient()
        self.disclient.loop.create_task(self.on_new_tweet())

    def restart_stream(self):
        """"""
        self.current_stream = tweepy.Stream(authenticator(), MyStreamListener())
        self.refilter_stream()

    def refilter_stream(self):
        """"""
        self.current_stream.filter(follow=get_users_to_stream(), is_async=True)

    @commands.Cog.listener()
    async def on_new_tweet(self):
        await self.disclient.wait_until_ready()
        while not self.disclient.is_closed():
            if self.current_stream.listener.new_tweet is not None:
                tweet = self.current_stream.listener.new_tweet
                await self.format_new_tweet(tweet)
            await asyncio.sleep(5)

    @commands.command(name='follow_twitter', aliases=['followtwitter', 'twitterfollow'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def twitter_follow(self, ctx, user_name):
        """Follows a twitter user, new tweets will be posted in the channel the command was called!
        Example: .follow_twitter <username or link>"""
        if 'twitter.com' in user_name:
            user_name = user_name.split('/')[-1]
        channel_id = ctx.channel.id
        add_channel(channel_id)
        user_id = self.client.get_twitter_user_id(user_name)
        if user_id:
            add_twitter_to_db(user_id)
        else:
            await ctx.send(embed=error_embed(f'Twitter user {user_name} not found!'))
        added = add_twitter_channel_to_db(channel_id, user_id)
        if added:
            await ctx.send(embed=success_embed(f'Followed twitter user {user_name}!'))
            self.refilter_stream()
        else:
            await ctx.send(embed=error_embed(f'Failed to follow twitter user {user_name}!'))

    @commands.command(name='unfollow_twitter', aliases=['unfollowtwitter', 'twitterunfollow'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def twitter_unfollow(self, ctx, user_name):
        """Unfollows a twitter user in this channel.
        Example: .unfollow_twitter <username or link>"""
        if 'twitter.com' in user_name:
            user_name = user_name.split('/')[-1]
        channel_id = ctx.channel.id
        user_id = self.client.get_twitter_user_id(user_name)
        if not user_id:
            await ctx.send(embed=error_embed(f'Twitter user {user_name} not found!'))
        removed = remove_twitter_user_from_db(channel_id, user_id)
        if removed:
            await ctx.send(embed=success_embed(f'Unfollowed twitter user {user_name}!'))
            self.refilter_stream()
        else:
            await ctx.send(embed=error_embed(f'Failed to unfollow twitter user {user_name}!'))

    async def format_new_tweet(self, tweet_data):
        """Formats a tweet into a nice discord embed"""
        twitter_id = tweet_data["user"]["id_str"]
        user_name = tweet_data["user"]["name"]
        twitter_at = f'@{tweet_data["user"]["screen_name"]}'
        title = f'{user_name} ({twitter_at})'
        profile_image = tweet_data["user"]["profile_image_url_https"]
        text = tweet_data["text"]
        if "extended_entities" in tweet_data:
            if len(tweet_data["extended_entities"]["media"]) > 1:
                images = []
                for media in tweet_data["extended_entities"]["media"]:
                    link = twitter_image_link_formatting(media["media_url_https"])
                    images.append(link)
                embed = discord.Embed(title=title,
                                      description=text,
                                      color=discord.Color.blue())
                embed.set_footer(text=f'Tweet by {twitter_at}',
                                 icon_url=profile_image)
                tweet = (embed, images)
            else:
                if tweet_data["extended_entities"]["media"][0]["type"] == 'video':
                    screen_name = tweet_data["user"]["screen_name"]
                    tweet_id = tweet_data["id_str"]
                    tweet = f'https://fxtwitter.com/{screen_name}/status/{tweet_id}'
                else:
                    l = tweet_data["extended_entities"]["media"][0]["media_url_https"]
                    image_url = twitter_image_link_formatting(l)
                    tweet = discord.Embed(title=title,
                                          description=text,
                                          color=discord.Color.blue())
                    tweet.set_image(url=image_url)
                    tweet.set_footer(text=f'Tweet by {twitter_at}',
                                     icon_url=profile_image)
        else:
            tweet = discord.Embed(title=title,
                                  description=text,
                                  color=discord.Color.blue())
            tweet.set_footer(text=f'Tweet by {twitter_at}',
                             icon_url=profile_image)
        self.current_stream.listener.new_tweet = None
        await self.send_new_tweet(tweet, twitter_id)

    async def send_new_tweet(self, tweet, twitter_id):
        """Sends tweet out to channels that are following that user"""
        channels = get_twitter_channels_following_user(twitter_id)
        for channel in channels:
            channel = self.disclient.get_channel(int(channel))
            if type(tweet) is tuple:
                await channel.send(embed=tweet[0])
                await channel.send('\n'.join(tweet[1]))
            else:
                if type(tweet) is str:
                    await channel.send(tweet)
                else:
                    await channel.send(embed=tweet)


def setup(disclient):
    disclient.add_cog(Twitter(disclient))
