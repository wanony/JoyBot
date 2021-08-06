CREATE TABLE users (
  UserId bigint NOT NULL,
  Xp int NOT NULL,
  Cont int NOT NULL,
  PRIMARY KEY (UserId)
);

CREATE TABLE moderators (
  UserId bigint NOT NULL,
  PRIMARY KEY (UserId),
  CONSTRAINT moderators_ibfk_1 FOREIGN KEY (UserId) REFERENCES users (UserId)
);

CREATE TABLE groupz (
  GroupId int NOT NULL AUTO_INCREMENT,
  RomanName varchar(255) NOT NULL,
  AddedBy bigint DEFAULT NULL,
  PRIMARY KEY (GroupId)
);

CREATE TABLE groupz_aliases (
  AliasID int NOT NULL AUTO_INCREMENT,
  GroupId int NOT NULL,
  Alias varchar(255) DEFAULT NULL,
  AddedBy bigint DEFAULT NULL,
  PRIMARY KEY (AliasID),
  CONSTRAINT groupz_aliases_ibfk_1 FOREIGN KEY (GroupId) REFERENCES groupz (GroupId) ON DELETE CASCADE
);

CREATE TABLE members (
  MemberId int NOT NULL AUTO_INCREMENT,
  GroupId int NOT NULL,
  RomanName varchar(255) NOT NULL,
  AddedBy bigint DEFAULT NULL,
  PRIMARY KEY (MemberId),
  KEY GroupId (GroupId),
  CONSTRAINT members_ibfk_1 FOREIGN KEY (GroupId) REFERENCES groupz (GroupId) ON DELETE CASCADE
);

CREATE TABLE member_aliases (
  AliasID int NOT NULL AUTO_INCREMENT,
  MemberId int NOT NULL,
  Alias varchar(255) DEFAULT NULL,
  AddedBy bigint DEFAULT NULL,
  PRIMARY KEY (AliasID),
  CONSTRAINT member_aliases_ibfk_1 FOREIGN KEY (MemberId) REFERENCES members (MemberId) ON DELETE CASCADE
);

CREATE TABLE tags (
  TagId int NOT NULL AUTO_INCREMENT,
  TagName varchar(255) NOT NULL,
  AddedBy bigint DEFAULT NULL,
  PRIMARY KEY (TagId)
);

CREATE TABLE tag_aliases (
  AliasID int NOT NULL AUTO_INCREMENT,
  TagId int NOT NULL,
  Alias varchar(255) DEFAULT NULL,
  AddedBy bigint DEFAULT NULL,
  PRIMARY KEY (AliasID),
  CONSTRAINT tag_aliases_ibfk_1 FOREIGN KEY (TagId) REFERENCES tags (TagId) ON DELETE CASCADE
);

CREATE TABLE links (
  LinkId int NOT NULL AUTO_INCREMENT,
  Link varchar(255) NOT NULL,
  AddedBy bigint DEFAULT NULL,
  PRIMARY KEY (LinkId)
);

CREATE TABLE link_tags (
  LinkId int NOT NULL,
  TagId int NOT NULL,
  PRIMARY KEY (LinkId, TagId),
  KEY TagId (TagId),
  CONSTRAINT link_tags_ibfk_1 FOREIGN KEY (LinkId) REFERENCES links (LinkId) ON DELETE CASCADE,
  CONSTRAINT link_tags_ibfk_2 FOREIGN KEY (TagId) REFERENCES tags (TagId) ON DELETE CASCADE
);

CREATE TABLE link_members (
  LinkId int NOT NULL,
  MemberId int NOT NULL,
  PRIMARY KEY (LinkId, MemberId),
  KEY MemberId (MemberId),
  CONSTRAINT link_members_ibfk_1 FOREIGN KEY (LinkId) REFERENCES links (LinkId) ON DELETE CASCADE,
  CONSTRAINT link_members_ibfk_2 FOREIGN KEY (MemberId) REFERENCES members (MemberId) ON DELETE CASCADE
);

CREATE TABLE custom_commands (
  CommandName varchar(255) CHARACTER SET utf32 COLLATE utf32_general_ci DEFAULT NULL,
  Command varchar(255) CHARACTER SET utf32 COLLATE utf32_general_ci DEFAULT NULL,
  AddedBy bigint DEFAULT NULL
);

CREATE TABLE channels (
  ChannelId int NOT NULL AUTO_INCREMENT,
  Channel bigint NOT NULL,
  PRIMARY KEY (ChannelId),
  UNIQUE (Channel)
);

CREATE TABLE linked_channels (
  ChannelId int NOT NULL,
  GroupId int NOT NULL,
  MemberId int NOT NULL,
  PRIMARY KEY (ChannelId), 
  FOREIGN KEY (ChannelId) REFERENCES channels(ChannelId),
  FOREIGN KEY (GroupId) REFERENCES groupz(GroupId),
  FOREIGN KEY (MemberId) REFERENCES members(MemberId)
);

CREATE TABLE reddit (
  RedditId int NOT NULL AUTO_INCREMENT,
  RedditName varchar(255) NOT NULL,
  PRIMARY KEY (RedditId)
);

CREATE TABLE reddit_channels (
  ChannelId int NOT NULL,
  RedditId int NOT NULL,
  PRIMARY KEY (ChannelId, RedditId),
  CONSTRAINT reddit_channels_ibfk_1 FOREIGN KEY (ChannelId) REFERENCES channels (ChannelId),
  CONSTRAINT reddit_channels_ibfk_2 FOREIGN KEY (RedditId) REFERENCES reddit (RedditId)
);

CREATE TABLE auditing_channels (
  ChannelId int NOT NULL,
  PRIMARY KEY (ChannelId),
  CONSTRAINT auditing_channels_ibfk_1 FOREIGN KEY (ChannelId) REFERENCES channels (ChannelId)
);

CREATE TABLE guilds (
  GuildId int NOT NULL AUTO_INCREMENT,
  Guild bigint NOT NULL,
  Prefix varchar(255) NOT NULL,
  TimerLimit int,
  PRIMARY KEY (GuildId),
  UNIQUE (Guild)
);

CREATE TABLE banned_words (
  WordId int NOT NULL AUTO_INCREMENT,
  Word varchar(255) NOT NULL,
  PRIMARY KEY (WordId),
  UNIQUE (Word)
);

CREATE TABLE guild_banned_words (
  WordId int NOT NULL,
  GuildId int NOT NULL,
  FOREIGN KEY (WordId) REFERENCES banned_words (WordId),
  FOREIGN KEY (GuildId) REFERENCES guilds (GuildId)
);

CREATE TABLE restricted_users (
	GuildId INT NOT NULL,
    UserId BIGINT NOT NULL,
    PRIMARY KEY (GuildId, UserId),
    FOREIGN KEY (GuildId) REFERENCES guilds(GuildId),
    FOREIGN KEY (UserId) REFERENCES users(UserId)
);

CREATE TABLE perma_users (
    UserId BIGINT NOT NULL,
    PRIMARY KEY (UserId),
    FOREIGN KEY (UserId) REFERENCES users(UserId)
);

CREATE TABLE twitter (
  TwitterId int NOT NULL AUTO_INCREMENT,
  Twitter bigint NOT NULL,
  PRIMARY KEY (TwitterId),
  UNIQUE (Twitter)
);

CREATE TABLE twitter_channels (
  ChannelId int NOT NULL,
  TwitterId int NOT NULL,
  PRIMARY KEY (ChannelId, TwitterId),
  FOREIGN KEY (ChannelId) REFERENCES channels (ChannelId),
  FOREIGN KEY (TwitterId) REFERENCES twitter (TwitterId)
);

CREATE TABLE instagram (
  InstagramId int NOT NULL AUTO_INCREMENT,
  Instagram bigint NOT NULL,
  PRIMARY KEY (InstagramId),
  UNIQUE (Instagram)
);

CREATE TABLE instagram_channels (
  ChannelId int NOT NULL,
  InstagramId int NOT NULL,
  PRIMARY KEY (ChannelId, InstagramId),
  FOREIGN KEY (ChannelId) REFERENCES channels (ChannelId),
  FOREIGN KEY (InstagramId) REFERENCES instagram (InstagramId)
);