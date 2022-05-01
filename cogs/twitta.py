import json
import nextcord as discord
from nextcord import SlashOption
from nextcord.abc import GuildChannel
from nextcord.utils import escape_markdown
import tweepy
from nextcord.ext import commands
from data import apis_dict, get_twitter_users_from_db, add_twitter_channel_to_db, remove_twitter_user_from_db, \
    add_twitter_to_db, add_channel, get_twitter_channels_following_user, get_all_twitter_channels_and_twitters
from embeds import error_embed, success_embed


def authenticator():
    """Returns authenticator."""
    auth = tweepy.OAuthHandler(apis_dict["twitter_key"], apis_dict["twitter_secret"])
    auth.set_access_token(apis_dict["twitter_access_token"], apis_dict["twitter_access_secret"])
    return auth


def get_users_to_stream():
    """Returns all users to stream tweets from."""
    users = get_twitter_users_from_db()
    return users


def twitter_image_link_formatting(link):
    """Formats link of tweeted image to return highest quality image."""
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
        """Create client."""
        self.client = tweepy.API(authenticator())

    def get_twitter_user(self, user_name):
        user = self.client.get_user(user_name)
        return user

    def get_twitter_user_name(self, twitter_id):
        user = self.client.get_user(twitter_id)
        name = user.screen_name
        return name


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, disclient):
        """Inherit and overwrite listener from Tweepy."""
        super().__init__()
        self.disclient = disclient

    def on_data(self, raw_data):
        self.disclient.loop.create_task(self.disclient.get_cog('Twitter').format_new_tweet(raw_data))

    def on_event(self, status):
        print(f"event: {status}")

    def on_connect(self):
        print('Twitter Stream Started!')

    def on_status(self, status):
        print(f"status: {status}")

    def on_error(self, status_code):
        if status_code == 420:
            print(f'Stream disconnected on Error Code {status_code}')
            return False  # return False disconnects, True tries reconnect
        print(status_code)
        return True

    def on_disconnect(self, notice):
        print(notice)
        Twitter.restart_stream(self.disclient)


class Twitter(commands.Cog):
    """Get new posts from your favourite Twitter users!
    """

    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient
        self.client = TwitterClient()
        self.current_stream = tweepy.Stream(authenticator(), MyStreamListener(self.disclient))
        self.current_stream.filter(follow=get_users_to_stream(), is_async=True)

    def restart_stream(self):
        """"""
        self.current_stream = tweepy.Stream(authenticator(), MyStreamListener(self.disclient))
        self.current_stream.filter(follow=get_users_to_stream(), is_async=True)

    @discord.slash_command(
        name="twitter",
        description="Handle Twitter integration",
        guild_ids=[755143761922883584]
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def twitter_handler(self,
                              interaction: discord.Interaction,
                              action: str = SlashOption(
                                  name="action",
                                  description="required action",
                                  choices=["follow", "unfollow", "list"],
                                  required=True
                              ),
                              username: str = SlashOption(
                                  name="username",
                                  description="twitch username or URL",
                                  required=False
                              ),
                              channel: GuildChannel = None):
        if action.lower() == "list":
            guild = interaction.guild
            chans = get_all_twitter_channels_and_twitters()
            chan_dict = {}
            for pair in chans:
                if pair[0] not in chan_dict:
                    chan_dict.update({pair[0]: [pair[-1]]})
                else:
                    chan_dict[pair[0]].append(pair[-1])
            msg = ''
            for channel in guild.channels:
                if channel.id in chan_dict:
                    for twitter in chan_dict[channel.id]:
                        twitter = self.client.get_twitter_user_name(twitter)
                        spacing = 39 - len(channel.name + twitter)
                        chan_str = f"`#{channel.name}{' ' * spacing}{twitter}`\n"
                        msg = msg + chan_str
            if msg == '':
                await interaction.response.send_message(
                    embed=error_embed('No Twitters followed in this server!'))
            else:
                add_to_start = f"`Channel Name{' ' * 19}Subreddit`\n"
                msg = add_to_start + msg
                embed = discord.Embed(title=f'Twitters Followed in {guild.name}!',
                                      description=msg,
                                      color=discord.Color.blue())
                await interaction.response.send_message(embed=embed)
        elif action.lower() == "follow":
            if 'twitter.com' in username:
                username = username.split('/')[-1]
            add_channel(channel.id)
            user = self.client.get_twitter_user(username)
            if user:
                add_twitter_to_db(user.id_str)
            else:
                await interaction.response.send_message(
                    embed=error_embed(f'Twitter user `{escape_markdown(username)}` not found!'))
            added = add_twitter_channel_to_db(channel.id, user.id_str)
            if added:
                icon_url = user.profile_image_url
                display_name = user.name
                link = f'https://twitter.com/{user.screen_name}'
                msg = f'This channel will now receive updates when {display_name} tweets at {link}'
                embed = discord.Embed(title=f'Successfully followed {escape_markdown(display_name)}',
                                      description=escape_markdown(msg),
                                      color=discord.Color.blue())
                embed.set_thumbnail(url=icon_url)
                await interaction.response.send_message(embed=embed)
                if user.id_str not in get_users_to_stream():
                    self.restart_stream()
            else:
                await interaction.response.send_message(
                    embed=error_embed(f'Failed to follow twitter user `{escape_markdown(username)}`!'))
        elif action.lower() == "unfollow":
            if 'twitter.com' in username:
                username = username.split('/')[-1]
            channel_id = channel.id
            user = self.client.get_twitter_user(username)
            if not user.id_str:
                # TODO make better twitter embed with images of display pics etc
                await interaction.response.send_message(
                    embed=error_embed(f'Twitter user `{escape_markdown(username)}` not found!'))
            removed = remove_twitter_user_from_db(channel_id, user.id_str)
            if removed:
                await interaction.response.send_message(
                    embed=success_embed(f'Unfollowed twitter user `{escape_markdown(username)}`!'))
            else:
                await interaction.response.send_message(
                    embed=error_embed(f'Failed to unfollow twitter user `{escape_markdown(username)}`!'))

    async def format_new_tweet(self, raw_data):
        """Formats a tweet into a nice discord embed"""
        tweet_data = json.loads(raw_data)
        try:
            twitter_id = tweet_data["user"]["id_str"]
        except KeyError:
            print('ValueError in formatting tweet')
            print(tweet_data)
            return
        user_name = escape_markdown(tweet_data["user"]["name"])
        twitter_at = f'@{escape_markdown(tweet_data["user"]["screen_name"])}'
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
                    link = tweet_data["extended_entities"]["media"][0]["media_url_https"]
                    image_url = twitter_image_link_formatting(link)
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
        await self.send_new_tweet(tweet, twitter_id)

    async def send_new_tweet(self, tweet, twitter_id):
        """Sends tweet out to channels that are following that user"""
        channels = get_twitter_channels_following_user(twitter_id)
        for channel in channels:
            channel = self.disclient.get_channel(int(channel))
            if isinstance(tweet, tuple):
                await channel.send(embed=tweet[0])
                await channel.send('\n'.join(tweet[1]))
            else:
                if isinstance(tweet, str):
                    await channel.send(tweet)
                else:
                    await channel.send(embed=tweet)


def setup(disclient):
    disclient.add_cog(Twitter(disclient))
