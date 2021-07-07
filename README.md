# Joy bot

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9a9bb9d798f645f09b90c12487745760)](https://app.codacy.com/gh/wanony/PublicBot?utm_source=github.com&utm_medium=referral&utm_content=wanony/PublicBot&utm_campaign=Badge_Grade_Settings)

An open source discord bot for storing embedding links powered by a MySQL/MariaDB database, with a focus on Kpop communities.
Links stored in the bot are accessable between servers and in direct messages.


### Features

- Gfycat, Youtube and Image link storage and retreval
- Group, Sub-group style SQL database 
- Tagging on links for easier references
- Custom Command creation
- Reddit updates from your favourite reddits
- Contribution leaderboards and levels
- Access user information and avatars
- Mod controls
- Auditing of links added
- ...And more to come!


### Join The Joy Discord

If you'd like to add Joy to your own server, join the Joy Discord Server!
- [Discord Invite Link](https://discord.gg/jmhgVbvau9)

More chat alternatives to come soon...


### Setup

If self hosting, it is required to setup a MySQL database and execute the script found in db_creation.
Many tutorials and options exist out there, so search around or try out MySQL on Windows or MariaDB on Linux/MacOS.

Ensure $PYTHON_DIR and $PYTHON_DIR/Scripts are on path.

`$ python -m install pipenv`  
`$ cd $SRC`  
`$ pipenv install`

To run

`$ pipenv run bot.py`