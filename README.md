# JoyBot
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/73ccb10ee6d84e85be71a1c397a7c1f8)](https://www.codacy.com/gh/wanony/PublicBot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=wanony/PublicBot&amp;utm_campaign=Badge_Grade)
[![Discord Server](https://discord.com/api/guilds/741066661221761135/embed.png)](https://discord.gg/bJvqnhg)

An open source discord bot using [discord.py](https://github.com/Rapptz/discord.py) and powered by a MySQL/MariaDB Database. Joy's main focus is storing and accessing embeddable links on the fly. Links stored in the bot are accessable between all servers and in direct messages!

# Features

- Gfycat, Youtube and Image link storage and retreval
- Group, Sub-group style SQL database
- User powered content addition
- Tagging on links for easier references
- Custom Command creation for memes and reactions
- Reddit updates from your favourite subreddits
- Twitter updates from your favourite tweeters
- Instagram updates from your favourite photographers
- Twitch livestream pings from your favourite streamers
- Contribution leaderboards and levels
- Access user information and avatars
- Mod controls
- Auditing of links added to the bot
- ...And more to come!

# Join The Joy Discord

If you'd like to add Joy to your own server, join the Joy Discord Server!

[![Discord Server](https://discord.com/api/guilds/741066661221761135/embed.png)](https://discord.gg/bJvqnhg)
-  [Discord Invite Link](https://discord.gg/jmhgVbvau9)

More chat alternatives to come soon...

# Setup

If self hosting, it is required to setup a MySQL database and execute the script found in db_creation.
Many tutorials and options exist out there, so search around or try out MySQL on Windows or MariaDB on Linux/MacOS.

Some JSON files are required in a sub directory jsons. Creation of 'apis.json' and backtracking may be painful.

Ensure $PYTHON_DIR and $PYTHON_DIR/Scripts are on path.

`$ python -m install pipenv`  
`$ cd $SRC`  
`$ pipenv install`

To run

`$ pipenv run bot.py`