import datetime

from nextcord import SlashOption
from nextcord.abc import GuildChannel
from twitchAPI.twitch import Twitch as Twitchy
from data import apis_dict, get_all_twitch_channels_to_check, get_channels_following_twitch_stream, \
    update_twitch_last_live, follow_twitch_channel_db, unfollow_twitch_channel_db, add_twitch_channel_to_db, \
    add_channel, get_all_twitch_followed_in_guild
import asyncio
from nextcord.ext import commands
import nextcord as discord

from embeds import success_embed, error_embed


class Twitch(commands.Cog):
    """Get live updates for your favourite twitch streamers
    """
    def __init__(self, disclient, twitch_id, twitch_sec):
        self.disclient = disclient
        self.disclient.loop.create_task(self.get_online_streams())
        self.twitch = Twitchy(twitch_id, twitch_sec,)
        self.twitch.authenticate_app([])
        self.time_format = '%Y-%m-%d %H:%M:%S'

    async def get_online_streams(self):
        await self.disclient.wait_until_ready()
        print('Looking for live Twitch streams!')
        while not self.disclient.is_closed():
            try:
                # print("checking twitch")
                check = get_all_twitch_channels_to_check(3)
                if not check:
                    await asyncio.sleep(60)
                    continue
                if len(check) > 100:
                    # need to split list into lengths of 100 in future
                    # get_streams only takes 100 inputs at a time
                    check = check[:99]
                ids = [str(x) for x in check.keys()]
                b = self.twitch.get_streams(user_id=ids)
                for stream in b["data"]:
                    c = self.twitch.get_users(user_ids=stream["user_id"])
                    linkend = c['data'][0]['login']
                    link = f"https://www.twitch.tv/{linkend}"
                    username = stream['user_name']
                    desc = stream['title']
                    msg = f"`{username}` is live! {link}"
                    image_url = f"""{stream['thumbnail_url'].format(
                                     width=852, height=480)}?{str(datetime.datetime.now().timestamp())}"""
                    embed = discord.Embed(title=msg,
                                          description=desc,
                                          color=discord.Color.purple())
                    embed.set_image(url=image_url)
                    embed.add_field(name='Playing',
                                    value=stream['game_name'])
                    check_time = datetime.datetime.strptime(stream['started_at'], '%Y-%m-%dT%H:%M:%SZ')
                    check_time.strftime(self.time_format)
                    if check[int(stream['user_id'])] != check_time:
                        update_twitch_last_live(stream['user_id'], check_time)
                    else:
                        continue
                    channels = get_channels_following_twitch_stream(stream['user_id'])
                    if not channels:
                        await asyncio.sleep(60)
                        continue
                    for chan in channels:
                        channel = self.disclient.get_channel(int(chan))
                        # TODO set ping roles up in the future
                        # gid = channel.guild.id
                        # rol = self.disclient.get_guild(gid).roles
                        # tr = discord.utils.get(rol, name="twitch")
                        await channel.send(embed=embed)  # content=tr.mention, for when roles are assigned
            except Exception as e:
                print(e)
            # delay 60 seconds before checking again
            await asyncio.sleep(60)

    @discord.slash_command(
        name="twitch",
        description="Handle Twitch integration",
        guild_ids=[755143761922883584]
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def twitch_handler(self,
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
        """Follows a twitch stream in this channel! Live updates will be posted here.
        .follow_twitch <username or link>"""
        if action.lower() == "list":
            list_embed = self.twitch_list_handler(interaction)
            await interaction.response.send_message(embed=list_embed)
            return
        if not channel:
            channel = interaction.channel
        if "twitch.tv" in username:
            stream = username.split("/")[-1].lower()
        else:
            stream = username.lower()
        username = self.twitch.get_users(logins=[stream])
        print(username)
        if not username:
            await interaction.response.send_message(
                embed=error_embed(f"Failed to find Twitch user {stream}!"))
            return
        for d in username["data"]:
            ayed = str(d["id"])
            add_channel(channel.id)
            add_twitch_channel_to_db(ayed)
            if action.lower() == "follow":
                followed = follow_twitch_channel_db(channel.id, ayed)
                if followed:
                    display_name = d['display_name']
                    profile_image = d['profile_image_url']
                    link = f"https://www.twitch.tv/{d['login']}"
                    msg = f'{channel.name} will now receive updates on when {display_name} goes live at {link}'
                    embed = discord.Embed(title=f'Successfully Followed {display_name}!',
                                          description=msg,
                                          color=discord.Color.purple())
                    embed.set_thumbnail(url=profile_image)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(
                        embed=error_embed(f"Failed to follow {stream} in {channel.name}!"))
            elif action.lower() == "unfollow":
                unfollowed = unfollow_twitch_channel_db(channel.id, ayed)
                if unfollowed:
                    await interaction.response.send_message(
                        embed=success_embed(f"Unfollowed {stream} in {channel.name}!"))
                else:
                    await interaction.response.send_message(
                        embed=error_embed(f"Failed to unfollow {stream} in {channel.name}!"))

    async def twitch_list_handler(self, interaction: discord.Interaction) -> discord.Embed:
        """Returns a list of all twitch users followed in this server!"""
        guild = interaction.guild
        chans = get_all_twitch_followed_in_guild()
        chan_dict = {}
        for pair in chans:
            if pair[0] not in chan_dict:
                chan_dict.update({pair[0]: [pair[-1]]})
            else:
                chan_dict[pair[0]].append(pair[-1])
        msg = ''
        for channel in guild.channels:
            if channel.id in chan_dict:
                for twitch in chan_dict[channel.id]:
                    twitch_str = str(twitch)
                    twitch = self.twitch.get_users(user_ids=[twitch_str])
                    twitch = twitch['data'][0]['login']
                    spacing = 39 - len(channel.name + twitch)
                    chan_str = f"`#{channel.name}{' ' * spacing}{twitch}`\n"
                    msg = msg + chan_str
        if msg == '':
            return error_embed('No Twitch streams followed in this server!')
        else:
            add_to_start = f"`Channel Name{' ' * 17}Twitch User`\n"
            msg = add_to_start + msg
            return discord.Embed(title=f'Twitch Streams Followed in {guild.name}!',
                                 description=msg,
                                 color=discord.Color.purple())


def setup(disclient):
    try:
        twitch_key = apis_dict['twitch_id']
        twitch_sec = apis_dict['twitch_secret']
        if twitch_key.strip() == "" or twitch_sec.strip() == "":
            print(f"Api key or secret missing, skipping loading cog twitch")
            return
        disclient.add_cog(Twitch(disclient, twitch_key, twitch_sec))
    except Exception as e:
        print(f"twitch cog could not be loaded")
        print(e)
