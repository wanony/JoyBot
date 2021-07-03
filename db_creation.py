from data import *

# Script file for creating the database used by the bot.

db = conn.connect(
    host="localhost",
    user=apis_dict["database_user"],
    passwd=apis_dict["database_password"],
    database="botdatabase",
    auth_plugin='mysql_native_password'
)

cursor = db.cursor()

# cursor.execute("CREATE DATABASE botdatabase")

# create users table

cursor.execute("""
    CREATE TABLE Users(
        UserId BIGINT NOT NULL,
        Xp INT NOT NULL,
        Cont INT NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (UserId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Users AS
        SELECT UserId, Xp, Cont FROM Users
        WHERE IsDeleted = 0;""")

# create moderator table

cursor.execute("""
    CREATE TABLE Moderators(
        UserId BIGINT NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (UserId),
        FOREIGN KEY (UserId) REFERENCES Users(UserId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Moderators AS
        SELECT UserId FROM Moderators
        WHERE IsDeleted = 0""")

# create groups table

cursor.execute("""
    CREATE TABLE Groupz(
        GroupId INT NOT NULL AUTO_INCREMENT,
        RomanName VARCHAR(255) NOT NULL,
        RawName VARCHAR(255) CHARACTER SET utf32,
        AddedBy BIGINT,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (GroupId),
        UNIQUE (RomanName)
        );
        """)

# WHEN ADDING TO ALIAS TABLES MAKE SURE;
# you add the group name as an alias,
# you will be able to make cleaner
# queries later.

cursor.execute("""
    CREATE TABLE Groupz_Aliases(
        GroupId INT NOT NULL,
        Alias VARCHAR(255),
        AddedBy BIGINT,
        PRIMARY KEY (GroupId),
        FOREIGN KEY (GroupId) REFERENCES Groupz (GroupId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Groupz AS
        SELECT GroupId, RomanName, RawName, AddedBy FROM Groupz 
        WHERE IsDeleted = 0""")

# create members table

cursor.execute("""
    CREATE TABLE Members(
        MemberId INT NOT NULL AUTO_INCREMENT,
        GroupId INT NOT NULL,
        RomanName VARCHAR(255) NOT NULL,
        RawName VARCHAR(255) CHARACTER SET utf32,
        AddedBy BIGINT,
        PRIMARY KEY (MemberId),
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        FOREIGN KEY (GroupId) REFERENCES Groupz(GroupId)
        );
        """)

cursor.execute("""
    CREATE TABLE Member_Aliases(
        MemberId INTO NOT NULL,
        Alias VARCHAR(255),
        AddedBy BIGINT,
        PRIMARY KEY (MemberId)
        FOREIGN KEY (MemberId) REFERENCES Members (MemberId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Members AS
        SELECT MemberId, GroupId, RomanName, RawName, AddedBy FROM Members 
        WHERE IsDeleted = 0""")

# create tags table

cursor.execute("""
    CREATE TABLE Tags(
        TagId INT NOT NULL AUTO_INCREMENT,
        TagName VARCHAR(255) NOT NULL,
        AddedBy BIGINT,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (TagId)
        );
        """)

cursor.execute("""
    CREATE TABLE Tag_Aliases(
        TagId INT NOT NULL,
        Alias VARCHAR(255),
        AddedBy BIGINT,
        PRIMARY KEY (TagId) REFERENCES Tags (TagId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Tags AS
        SELECT TagId, TagName, AddedBy FROM Tags 
        WHERE IsDeleted = 0""")

# create links table

cursor.execute("""
    CREATE TABLE Links(
        LinkId INT NOT NULL AUTO_INCREMENT,
        Link VARCHAR(255) NOT NULL,
        AddedBy BIGINT,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (LinkId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Links AS
        SELECT LinkId, Link, AddedBy FROM Links
        WHERE IsDeleted = 0""")

# create link tags table

cursor.execute("""
    CREATE TABLE Link_Tags(
        LinkId INT NOT NULL,
        TagId INT NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (LinkId, TagId),
        FOREIGN KEY (LinkId) REFERENCES Links(LinkId),
        FOREIGN KEY (TagId) REFERENCES Tags(TagId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Link_Tags AS
        SELECT LinkId, TagId FROM Link_Tags
        WHERE IsDeleted = 0""")

# create link members table

cursor.execute("""
    CREATE TABLE Link_Members(
        LinkId INT NOT NULL,
        MemberId INT NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (LinkId, MemberId),
        FOREIGN KEY (LinkId) REFERENCES Links(LinkId),
        FOREIGN KEY (MemberId) REFERENCES Members(MemberId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Link_Members AS
        SELECT LinkId, MemberId FROM Link_Members
        WHERE IsDeleted = 0""")

# create table for custom commands/memes

cursor.execute("""
    CREATE TABLE Custom_Commands(
        CommandName VARCHAR(255) CHARACTER SET utf32,
        Command VARCHAR(255) CHARACTER SET utf32,
        AddedBy BIGINT,
        IsDeleted TINYINT NOT NULL DEFAULT 0
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Custom_Commands AS
        SELECT CommandName, Command, AddedBy FROM Custom_Commands
        WHERE IsDeleted = 0""")

# create table for channels

cursor.execute("""
    CREATE TABLE Channels(
        ChannelId INT NOT NULL AUTO_INCREMENT,
        Channel BIGINT NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (ChannelId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Channels AS
        SELECT ChannelId, Channel FROM Channels
        WHERE IsDeleted = 0""")

# create reddit table

cursor.execute("""
    CREATE TABLE Reddit(
        RedditId INT NOT NULL AUTO_INCREMENT,
        RedditName VARCHAR(255) NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (RedditId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Reddit AS
        SELECT RedditId, RedditName FROM Reddit
        WHERE IsDeleted = 0""")

# create linking tables for channels and other things

cursor.execute("""
    CREATE TABLE Reddit_Channels(
        ChannelId INT NOT NULL,
        RedditId INT NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (ChannelId, RedditId),
        FOREIGN KEY (ChannelId) REFERENCES Channels(ChannelId),
        FOREIGN KEY (RedditId) REFERENCES Reddit(RedditId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Reddit_Channels AS
        SELECT ChannelId, RedditId FROM Reddit_Channels
        WHERE IsDeleted = 0""")

cursor.execute("""
    CREATE TABLE Auditing_Channels(
        ChannelId INT NOT NULL,
        IsDeleted TINYINT NOT NULL DEFAULT 0,
        PRIMARY KEY (ChannelId),
        FOREIGN KEY (ChannelId) REFERENCES Channels(ChannelId)
        );
        """)

cursor.execute("""
    CREATE VIEW Active_Auditing_Channels AS
        SELECT ChannelId FROM Auditing_Channels
        WHERE IsDeleted = 0""")


db.commit()
cursor.close()
