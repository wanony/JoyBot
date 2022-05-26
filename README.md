# JoyBot
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/73ccb10ee6d84e85be71a1c397a7c1f8)](https://www.codacy.com/gh/wanony/PublicBot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=wanony/PublicBot&amp;utm_campaign=Badge_Grade)
[![Discord Server](https://discord.com/api/guilds/741066661221761135/embed.png)](https://discord.gg/bJvqnhg)

A free and open source Discord bot using [nextcord](https://github.com/nextcord/nextcord) and powered by a MySQL/MariaDB Database. Joy's main focus is storing and accessing embeddable links on the fly. Links stored in the bot are accessable between all servers and in direct messages!

The main goal of the Joy Discord bot is to maximise the interaction in Discord servers.

This is achieved by providing a range of media formats and commands that can bring all the fun to the table, without having to leave Discord.

# Features

- Gfycat, YouTube and Image link storage and retreval
- Support for Discord 2.0 features such as buttons and slash commands
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

Currently, Joy is under the conversion to slash commands, with a planned update date of March 31st!

# Joy's Commands

Joy has a number of commands that fall into different categories. 


MODERATOR COMMANDS [M]: Some commands are only able to be used by Moderators who have been approved in the Joy discord, these will be marked with [M]. 
If you'd like to become a moderator, join the Joy discord server to find out more.


OPTIONAL ARGUMENTS *: Some commands have optional arguments, these will be marked with a * in the usage column.

### Adding to Joy

These commands add content to Joy's database.

| Command         | Arguments         | Description                                                                                                     |
|-----------------|-------------------|-----------------------------------------------------------------------------------------------------------------|
| /addcustom      | Name, Link        | Adds a custom command with the name provided. When using /custom, the name can be called and the link returned. |
| /addgroup  [M]  | Name              | Adds a new group to Joy's database.                                                                             |
| /addidol [M]    | Group, Name       | Adds an idol to the group provided, allowing links to be added to them.                                         |
| /addlink        | Group, Idol, Link | Adds a link to the specified idol. This will then be stored on Joy's database.                                  |
| /createtag  [M] | Name              | Adds a new tag with the given name.                                                                             |

### Remove From Joy

Removes content from Joy's Database. All of these commands are limited to moderators.

| Command            | Usage             | Description                                                 |
|--------------------|-------------------|-------------------------------------------------------------|
| /deletecommand [M] | Name              | Deletes a custom command.                                   |
| /deletegroup   [M] | Group             | Deletes a group and all idols added to it.                  |
| /deleteidol    [M] | Group, Idol       | Deletes an idol from a group.                               |
| /deletelink    [M] | Group, Idol, Link | Deletes a link from the specified idol.                     |
| /deletetag     [M] | Tag               | Deletes a tag from Joy, and untags all links related to it. |
| /removetag     [M] | Tag, Link         | Removes a tag from a link added to Joy.                     |

### See Joy's content

These commands will give you an idea of what is available on Joy's database. They all return information regarding this.

| Command         | Usage         | Description                                                                                                                                                                                                                                                                        |
|-----------------|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| /dates          | None          | Returns a list of all dates added to Joy. These dates are tagged against links added.                                                                                                                                                                                              |
| /info           | Group*, Idol* | Returns information regarding Joy's content. If no arguments are provided, then a list of all groups is returned. If a group is specified, then information regarding that group is returned. If a group and idol are specified, then information regarding that idol is returned. |
| /listcustom     | None          | Returns a list of all custom commands added to Joy.                                                                                                                                                                                                                                |
| /tags           | None          | Returns a list of all tags added to Joy.                                                                                                                                                                                                                                           |

### Get Joy's Content

These commands will provide the user with links added to Joy's database.

| Command | Usage        | Description                                                            |
|---------|--------------|------------------------------------------------------------------------|
| /fancam | Group, Idol  | Returns a link of a fancam of the specified idol, if any are added.    |
| /gfy    | Group, Idol* | Returns a gfycat link of the specified idol, if there are any added.   |
| /image  | Group, Idol  | Returns an image of the specified idol, if they are any added.         |
| /random | None         | Returns a completely random link, that could belong to any group/idol. |

### Timer Commands

Timer's provide users with links periodically, saving time from having to enter commands repeatedly.

| Command     | Usage                                                 | Description                                                                                                                        |
|-------------|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| /timer      | Group, Idol, Duration(minutes)\*, Interval(seconds)\* | Sends gfycat links of the specified idol for a set time (the Duration argument). These links are sent every 10 seconds (Interval). |
| /stoptimer  | Timer ID                                              | Stops a specified timer.                                                                                                           |
| /viewtimers | None                                                  | See a list of all your active timers.                                                                                              |

### Server Specific

These commands only affect servers. Server admins can configure and moderate Joy's use in their servers.

| Command         | Arguments         | Description                                                                                                                               |
|-----------------|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| /addauditing    | Channel           | Will message this channel with every new link added to Joy.                                                                               |
| /removeauditing | Channel           | Removes the above auditing function from a channel.                                                                                       |
| /forcestoptimer | User              | Stops all timers belonging to a user in your Discord server. You need permissions to delete messages in the server to issue this command. |
| /restrictuser   | User              | Stops a user from being able to interact with Joy in your Discord server.                                                                 |
| /setmaxtimer    | Duration(minutes) | Sets the maximum allowed time for the timer command to use in your Discord server.                                                        |
| /unrestrictuser | User              | Unrestricts the user from the limitations as above.                                                                                       |


### Miscellaneous Commands

Commands that are not applicable to other categories listed above.

| Command         | Usage        | Description                                                                                                                                                                                                                                      |
|-----------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| /custom         | Name         | Receive the response from a custom created command.                                                                                                                                                                                              |
| /leaderboard    | Type         | See the leaderboard of different types on Joy. These types are 'contribution', 'idols' and 'groups'. Contribution shows the users who have added the most to Joy. Groups and Idols will show the Groups/Idols with the most links added to them. |
| /report         | Link, Reason | Report a link added to Joy that is problematic, it will be checked and removed by the moderator team.                                                                                                                                            |
| /suggest        | Suggestion   | Provide a suggestion to a new feature or change to Joy.                                                                                                                                                                                          |
| /totallinks     | None         | See the total number of links added to Joy!                                                                                                                                                                                                      |

# Setup

If self-hosting, it is required to set up a MySQL or MariaDB database and execute the script found in db_creation.
Many tutorials and options exist out there, so search around or try out MySQL on Windows or MariaDB on Linux/macOS.

Some JSON files are required in a subdirectory jsons. Creation of 'apis.json' and backtracking may be painful, but this
setup should be handled automatically now.

Ensure $PYTHON_DIR and $PYTHON_DIR/Scripts are on path.

`$ python -m install pipenv`  
`$ cd $SRC`  
`$ pipenv install`

To run

`$ pipenv run bot.py`