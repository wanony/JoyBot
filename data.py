import json
import mysql.connector as conn
import mysql.connector.errors

with open('directories.json') as direc:
    direc_dict = json.load(direc)
with open(direc_dict["apis"], 'r') as apis:
    apis_dict = json.load(apis)

command_prefix = apis_dict["command_prefix"]

with open(direc_dict["recents"], 'r') as recen:
    recent_dict = json.load(recen)
with open(direc_dict["mods"], 'r') as mods:
    mods_dict = json.load(mods)


def check_user_is_mod(ctx):
    return find_moderator(ctx.author.id)


def check_user_is_owner(ctx):
    if ctx.author.id in mods_dict["owners"]:
        return True
    else:
        return False


db = conn.connect(
    host="localhost",
    user=apis_dict["database_user"],
    passwd=apis_dict["database_password"],
    database="botdatabase",
    buffered=True
)

# --- CUSTOM COMMANDS --- #


def add_command(name, link, added_by):
    """Add a new custom command to the database"""
    cursor = db.cursor()
    sql = "INSERT INTO Custom_Commands(CommandName, Command, AddedBy) VALUES (%s, %s, %s);"
    val = (name, link, added_by)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def get_commands():
    """returns a dictionary of all commands in the database"""
    cursor = db.cursor()
    sql = "SELECT CommandName, Command FROM Custom_Commands ORDER BY CommandName;"
    cursor.execute(sql)
    result = dict(cursor.fetchall())
    cursor.close()
    return result


def find_command(command_name):
    """Finds a specific command by name in the database"""
    cursor = db.cursor()
    sql = """SELECT CommandName FROM Custom_Commands
                WHERE CommandName = %s"""
    val = command_name
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def remove_command(name):
    """Removes a command by name from the database"""
    cursor = db.cursor()
    # sql = """UPDATE Custom_Commands
    #         SET
    #             Custom_Commands.IsDeleted = 1
    #         WHERE
    #             Custom_Commands.CommandName = %s;"""
    sql = """DELETE FROM Custom_Commands
                WHERE CommandName = %s"""
    value = (name,)
    cursor.execute(sql, value)
    db.commit()
    row_count = cursor.rowcount
    cursor.close()
    return row_count > 0


# --- LINK COMMANDS --- #


def add_link(link, added_by):
    """Adds a link to the database"""
    cursor = db.cursor()
    sql = "INSERT INTO Links(Link, AddedBy) VALUES (%s, %s);"
    values = (link, added_by)
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(e)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount


def count_links():
    """returns a count of all links, groups, and members"""
    cursor = db.cursor()
    sql = """SELECT
              (SELECT COUNT(*) FROM links) as link_count, 
              (SELECT COUNT(*) FROM groupz) as group_count,
              (SELECT COUNT(*) FROM members) as member_count"""
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    return result


def get_link_id(link):
    """Returns a links unique ID in the database"""
    cursor = db.cursor()
    sql = "SELECT LinkId FROM Links WHERE Link = %s"
    val = (link,)
    cursor.execute(sql, val)
    link_id = cursor.fetchone()[0]
    cursor.close()
    return link_id


def remove_link(group, member, link):
    """Removes a link from a member"""
    cursor = db.cursor()
    # sql = """UPDATE Links, Link_Members, Link_Tags
    #             SET
    #                 Links.IsDeleted = 1,
    #                 Links_Members.IsDeleted = 1,
    #                 Links_Tags.IsDeleted = 1
    #             WHERE
    #                 Links.LinkId = %s
    #                 AND
    #                 Links.LinkId = Link_Tags.LinkId
    #                 AND
    #                 Link_Members.MemberId = %s
    #                 AND
    #                 Link_Members.LinkId = Links.LinkId;
    #         """
    # sql = """DELETE Link_Members FROM Link_Members
    #             INNER JOIN Links
    #                 ON Link_Members.LinkId = Links.LinkId
    #             INNER JOIN Members
    #                 ON Members.MemberId = Link_Members.MemberId
    #             INNER JOIN Groupz
    #                 ON Groupz.GroupId = Members.GroupId
    #             WHERE
    #                 Groupz.RomanName = %s
    #                 AND
    #                 Members.RomanName = %s
    #                 AND
    #                 Links.Link = %s
    #                 """
    # sql = """DELETE link_members, link_tags, links  FROM links
    #             left JOIN groupz
    #                 ON groupz.RomanName = %s
    #             left JOIN members
    #                 ON members.RomanName = %s
    #             left JOIN link_members
    #                 ON members.MemberId = link_members.MemberId
    #             left JOIN link_tags
    #                 ON link_tags.LinkId = link_members.linkId
    #             WHERE links.Link = %s;"""
    sql = """DELETE link_members, link_tags, links  FROM links
                left JOIN groupz_aliases
                    ON groupz_aliases.Alias = %s
                left JOIN groupz
                    ON groupz.GroupId = groupz_aliases.GroupId
                left JOIN member_aliases
                    ON member_aliases.Alias = %s
                left JOIN members
                    ON members.MemberId = member_aliases.MemberId
                left JOIN link_members 
                    ON members.MemberId = link_members.MemberId
                left JOIN link_tags 
                    ON link_tags.LinkId = link_members.linkId
                WHERE links.Link = %s;"""
    value = (group, member, link)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def add_link_to_member(member_id, link_id):
    cursor = db.cursor()
    sql = """INSERT INTO Link_Members(LinkId, MemberId) VALUES (%s, %s);"""
    values = (link_id, member_id)
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(e)
        return False
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


# --- TAG COMMANDS --- #


def add_tag(tag_name, added_by):
    """Adds a new tag to the database"""
    cursor = db.cursor()
    sql = "INSERT INTO Tags(TagName, AddedBy) VALUES (%s, %s);"
    value = (tag_name, added_by)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def add_tag_alias(tag_id, alias, added_by):
    cursor = db.cursor()
    sql = "INSERT INTO Tag_Aliases(TagId, Alias, AddedBy) VALUES (%s, %s, %s);"
    values = (tag_id, alias, added_by)
    cursor.execute(sql, values)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def get_all_tag_names():
    """returns all tag names"""
    cursor = db.cursor()
    sql = "SELECT TagName FROM Tags ORDER BY TagName"
    # sql = """SELECT Alias FROM Tag_Aliases ORDER BY Alias"""
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all_alias_of_tag(tag):
    """returns all aliases of tag from db"""
    cursor = db.cursor()
    sql = """select alias from tag_aliases
             left join tags
             on tags.TagId = tag_aliases.TagId
             where tag_aliases.alias = %s"""
    val = (tag,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


def add_tag_alias_db(tag, alias, user_id):
    """adds a new alias to an existing tag"""
    cursor = db.cursor()
    sql = """INSERT INTO tag_aliases(TagId, Alias, AddedBy)
             VALUES ((SELECT TagId FROM Tags WHERE TagName = %s), %s, %s)"""
    val = (tag, alias, user_id)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_tag_alias_db(tag, alias):
    """adds a new alias to an existing tag"""
    cursor = db.cursor()
    sql = """delete from tag_aliases where tag_aliases.TagId = ANY(select tags.TagId from tags WHERE TagName = %s)
             AND tag_aliases.Alias = %s"""
    val = (tag, alias)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_tag_id(tag_name):
    """Returns the unique ID of a tag by name"""
    cursor = db.cursor()
    sql = "SELECT TagId FROM Tags WHERE TagName = %s"
    # sql = """SELECT tags.TagId FROM Tags
    #             left join tag_aliases
    #                 on tag_aliases.TagId = tags.TagId
    #             WHERE tag_aliases.Alias = %s"""
    val = (tag_name,)
    cursor.execute(sql, val)
    tag_id = cursor.fetchone()
    cursor.close()
    return tag_id


def find_tags_on_link(link):
    """Returns a dict of tagnames and IDs that are on a link"""
    cursor = db.cursor()
    sql = """SELECT TagName, TagId, Links.LinkId 
             FROM Tags, Links
                WHERE
                    Links.Link = %s
                    AND
                    Tags.LinkId = Links.LinkId;"""
    val = (link,)
    cursor.execute(sql, val)
    tags = dict(cursor.fetchall())
    cursor.close()
    return tags


def remove_tag(tag):
    cursor = db.cursor()
    # sql = """UPDATE Tags, Link_Tags
    #             SET
    #                 Tags.IsDeleted = 1,
    #                 Link_Tags.IsDeleted = 1
    #             WHERE
    #                 Tags.TagId = %s
    #                 AND
    #                 Link_Tags.TagId = Tags.TagId;
    #                 """
    # sql = """DELETE tags, link_tags FROM tags
    #             INNER JOIN link_tags ON tags.TagId = link_tags.TagId
    #             WHERE tags.TagName = %s;"""
    sql = "DELETE FROM tags WHERE TagName = %s"
    value = (tag,)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def add_link_tags(link, tag_name):
    cursor = db.cursor()
    # sql = """INSERT INTO Link_Tags(LinkId, TagId) SELECT Links.LinkId, Tags.TagId FROM Links
    #          LEFT JOIN Tags ON Tags.TagName = %s
    #          WHERE Links.Link = %s"""
    sql = """INSERT INTO Link_Tags(LinkId, Tags.TagId) SELECT Links.LinkId, Tags.TagId FROM Links
             LEFT JOIN Tag_Aliases ON Tag_Aliases.Alias = %s
             LEFT JOIN Tags ON Tags.TagId = Tag_Alaises.TagId
             WHERE Links.Link = %s"""
    values = (tag_name, link)
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(e)
        return False
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_tag_from_link(link, tag):
    cursor = db.cursor()
    # sql = """UPDATE Link_Tags
    #             INNER JOIN Links ON
    #                 Links.LinkId = Link_Tags.LinkId
    #             INNER JOIN Tags ON
    #                 Tags.TagId = Link_Tags.TagId
    #             SET
    #                 Link_Tags.IsDeleted = 1
    #             WHERE
    #                 Links.Link = %s
    #                 AND
    #                 Tags.TagName = %s;"""
    sql = """DELETE FROM Link_Tags
          WHERE LinkId = ANY(SELECT LinkId FROM Links WHERE Link = %s) 
          AND TagId = ANY(SELECT TagId FROM Tags WHERE TagName = %s)"""
    values = (link, tag)
    cursor.execute(sql, values)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def get_links_with_tag(tag_name):
    cursor = db.cursor()
    sql = """select link from links
                inner join link_tags on link_tags.LinkId = links.LinkId
                inner join tags on tags.TagId = link_tags.TagId
                where tags.TagName = %s"""
    val = (tag_name,)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    result = cursor.fetchall()
    cursor.close()
    return result


def member_link_count(group_name, member_name):
    cursor = db.cursor()
    sql = """select count(*) from link_members
                inner join members on members.RomanName = %s
                inner join groupz on groupz.RomanName = %s
                where groupz.GroupId = members.GroupId
                and members.MemberId = link_members.MemberId"""
    values = (member_name, group_name)
    cursor.execute(sql, values)
    result = cursor.fetchone()
    cursor.close()
    return result


# --- GROUPZ COMMANDS --- #


def add_group(group_name, added_by):
    cursor = db.cursor()
    sql = "INSERT INTO Groupz(RomanName, AddedBy) VALUES (%s, %s);"
    values = (group_name, added_by)
    try:
        cursor.execute(sql, values)
    except mysql.connector.errors.IntegrityError:
        return None
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_group(group):
    cursor = db.cursor()
    # sql = """UPDATE Groupz, Members, Link_Members, Links
    #             SET
    #                 Groupz.IsDeleted = 1,
    #                 Members.IsDeleted = 1,
    #                 Link_Members.IsDeleted = 1,
    #                 Links.IsDeleted = 1
    #             WHERE
    #                 Groupz.RomanName = %s
    #                 AND
    #                 Members.GroupId = Groupz.GroupId
    #                 AND
    #                 Link_Members.MemberId = Members.MemberId
    #                 AND
    #                 Links.LinkId = Link_Members.LinkId;"""
    # sql = """DELETE groupz, members, member_aliases, groupz_aliases, link_members, link_tags, links FROM groupz
    #             left JOIN members
    #                 ON members.GroupId  is not null and  members.GroupId = groupz.GroupId
    #             left JOIN member_aliases
    #                 ON member_aliases.MemberId  is not null and member_aliases.MemberId = members.MemberId
    #             left JOIN groupz_aliases
    #                 ON  groupz_aliases.GroupId is not null and groupz_aliases.GroupId = groupz.GroupId
    #             left JOIN link_members
    #                 ON members.MemberId is not null and members.MemberId = link_members.MemberId
    #             left JOIN links
    #                 ON links.LinkId is not null and links.LinkId = link_members.LinkId
    #             left JOIN link_tags
    #                 ON links.LinkId is not null and links.LinkId = link_tags.LinkId
    #             WHERE groupz.RomanName = %s;"""
    sql = "DELETE FROM groupz WHERE RomanName = %s;"
    values = (group,)
    try:
        cursor.execute(sql, values)
    except mysql.connector.errors.IntegrityError:
        return None
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_group_id(group_name):
    cursor = db.cursor()
    sql = """SELECT Groupz.GroupId FROM Groupz 
                left join groupz_aliases
                    on groupz_aliases.Alias = %s
                where Groupz.GroupId = groupz_aliases.GroupId;"""
    value = (group_name,)
    try:
        cursor.execute(sql, value)
    except Exception as e:
        print(e)
        return None
    g_id = cursor.fetchone()
    cursor.close()
    return g_id


def find_group_id_and_name(group_name):
    cursor = db.cursor()
    sql = """SELECT Groupz.GroupId, Groupz.RomanName FROM Groupz 
                left join groupz_aliases
                    on groupz_aliases.Alias = %s
                where Groupz.GroupId = groupz_aliases.GroupId;"""
    value = (group_name,)
    try:
        cursor.execute(sql, value)
    except Exception as e:
        print(e)
        return None
    name_and_g_id = cursor.fetchone()
    cursor.close()
    return name_and_g_id


def find_group_and_member_id(group_name, member_name):
    cursor = db.cursor()
    sql = """select groupz.GroupId, members.MemberId from groupz, members
             where groupz.RomanName = %s
             and members.RomanName = %s"""
    values = (group_name, member_name)
    cursor.execute(sql, values)
    result = cursor.fetchone()
    cursor.close()
    return result


def get_groups():
    cursor = db.cursor()
    sql = """SELECT RomanName FROM Groupz
                ORDER BY RomanName"""
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def add_group_alias_db(group_name, alias, user_id):
    cursor = db.cursor()
    sql = """INSERT INTO groupz_aliases(GroupId, Alias, AddedBy) 
             VALUES ((SELECT GroupId FROM groupz WHERE RomanName = %s), %s, %s)"""
    val = (group_name, alias, user_id)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_group_alias_db(group_name, alias):
    cursor = db.cursor()
    sql = """delete from groupz_aliases where groupz_aliases.GroupId = ANY(
             select groupz.GroupId from groupz WHERE RomanName = %s)
             AND groupz_aliases.Alias = %s"""
    val = (group_name, alias)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def get_group_aliases(group_name):
    cursor = db.cursor()
    sql = "select Alias from Groupz_Aliases WHERE GroupId = %s"
    val = (group_name,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


# --- Members Commands --- #


def add_member(group_name, member_name, addedby):
    cursor = db.cursor()
    sql = """INSERT INTO Members(GroupId, RomanName, AddedBy)
                VALUES ((SELECT Groupz.GroupId FROM Groupz WHERE Groupz.RomanName = %s),
                         %s, %s);"""
    values = (group_name, member_name, addedby)
    try:
        cursor.execute(sql, values)
    except mysql.connector.errors.IntegrityError:
        return None
    db.commit()
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def remove_member(group_id, member_name):
    cursor = db.cursor()
    # sql = """UPDATE Members, Link_Members, Links
    #             SET
    #                 Members.IsDeleted = 1,
    #                 Link_Members.IsDeleted = 1,
    #                 Links.IsDeleted = 1
    #             WHERE
    #                 Members.MemberId = %s
    #                 AND
    #                 Link_Members.MemberId = Members.MemberId
    #                 AND
    #                 Links.LinkId = Link_Members.LinkId;"""
    # sql = """DELETE Members, Link_Members, Links FROM Members
    #             left JOIN link_members
    #                 ON members.MemberId = link_members.MemberId
    #             left JOIN links
    #                 ON links.LinkId = link_members.LinkId
    #             WHERE members.RomanName = %s
    #             AND members.GroupId = %s;"""
    sql = "DELETE FROM Members WHERE RomanName = %s AND GroupId = %s"
    values = (member_name, group_id)
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(e)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_member_id(group_id, member_name):
    cursor = db.cursor()
    # sql = "SELECT MemberId FROM Members WHERE RomanName = (%s) AND GroupId = (%s)"
    sql = """SELECT members.MemberId FROM Members
                left join member_aliases
                    on member_aliases.MemberId = members.MemberId
                WHERE alias = (%s) AND members.GroupId = (%s)"""
    val = (member_name, group_id)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    member_id = cursor.fetchone()
    cursor.close()
    return member_id


def find_member_id_and_name(group_id, member_name):
    cursor = db.cursor()
    # sql = "SELECT MemberId FROM Members WHERE RomanName = (%s) AND GroupId = (%s)"
    sql = """SELECT members.MemberId, members.RomanName FROM Members
                left join member_aliases
                    on member_aliases.MemberId = members.MemberId
                WHERE alias = (%s) AND members.GroupId = (%s)"""
    val = (member_name, group_id)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    member_id_and_name = cursor.fetchone()
    cursor.close()
    return member_id_and_name


def add_member_alias_db(group, idol, alias, user_id):
    cursor = db.cursor()
    sql = """INSERT INTO member_aliases(MemberId, Alias, AddedBy) VALUES (
             (SELECT MemberId FROM members
             left join groupz on groupz.GroupId = members.GroupId
             left join groupz_aliases on groupz.GroupId = groupz_aliases.GroupId
             WHERE groupz_aliases.Alias = %s AND members.RomanName = %s),
             %s, %s)"""
    val = (group, idol, alias, user_id)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    db.commit()
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def remove_member_alias_db(group, idol, alias):
    cursor = db.cursor()
    sql = """delete from member_aliases 
             where member_aliases.MemberId = ANY(
             select members.MemberId from members
             left join groupz on groupz.GroupId = members.GroupId 
             left join groupz_aliases on groupz.GroupId = groupz_aliases.GroupId
             WHERE members.RomanName = %s AND groupz_aliases.Alias = %s
             )
             AND member_aliases.Alias = %s"""
    val = (idol, group, alias)
    cursor.execute(sql, val)
    db.commit()
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def find_member_aliases(member_id):
    cursor = db.cursor()
    sql = "select Alias from member_aliases where MemberId = %s ORDER BY Alias"
    val = (member_id,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_members_of_group(group_name):
    """Returns a dict of members of a group"""
    cursor = db.cursor()
    sql = """SELECT Members.RomanName FROM Members
                INNER JOIN Groupz ON Groupz.RomanName = %s
                WHERE Members.GroupId = Groupz.GroupId;"""
    val = (group_name,)
    cursor.execute(sql, val)
    members = cursor.fetchall()
    cursor.close()
    return members


def get_members_of_group_by_group_id(group_id):
    cursor = db.cursor()
    sql = """SELECT Members.RomanName FROM Members
                INNER JOIN Groupz ON Groupz.GroupId = %s
                WHERE Members.GroupId = Groupz.GroupId;"""
    val = group_id
    cursor.execute(sql, val)
    members = cursor.fetchall()
    cursor.close()
    return members


def get_member_links(group_id, member_name):
    cursor = db.cursor()
    sql = """select Link from Links
                left join link_members 
                    on links.LinkId = link_members.LinkId
                left join groupz 
                    on groupz.GroupId = %s
                left join members 
                    on members.MemberId = link_members.MemberId
                left join member_aliases
                    on members.MemberId = member_aliases.MemberId
                where member_aliases.Alias = %s"""
    vals = (group_id, member_name)
    try:
        cursor.execute(sql, vals)
    except Exception as e:
        print(e)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_members_of_group_and_link_count(group_id):
    cursor = db.cursor()
    sql = """SELECT Members.RomanName,
                (SELECT COUNT(*) FROM link_members WHERE link_members.MemberId = members.MemberId)
                FROM Members
                INNER JOIN groupz ON groupz.GroupId = %s
                WHERE Members.GroupId = Groupz.GroupId
                ORDER BY Members.RomanName"""
    val = (group_id,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_member_links_with_tag(group_id, member_name, tag):
    cursor = db.cursor()
    sql = """select Link from Links
             left join link_members 
                on links.LinkId = link_members.LinkId
             left join groupz 
                on groupz.GroupId = %s
             left join members 
                on members.MemberId = link_members.MemberId
            left join member_aliases
                on member_aliases.MemberId = members.MemberId
            left join link_tags 
                on link_tags.LinkId = Links.LinkId 
            left join tags 
                on tags.TagId = link_tags.TagId
            left join tag_aliases
                on tag_aliases.TagId = tags.TagId
            WHERE tag_aliases.Alias = %s
            AND member_aliases.Alias = %s
            """
    vals = (group_id, member_name, tag)
    cursor.execute(sql, vals)
    result = cursor.fetchall()
    cursor.close()
    return result


def count_links_of_member(member_id):
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM Link_Members WHERE MemberId = (%s)"
    val = (member_id,)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    result = cursor.fetchone()[0]
    return result


def last_three_links(member_id):
    cursor = db.cursor()
    sql = """SELECT Link FROM Links
                INNER JOIN Link_Members ON Links.LinkId = Link_Members.LinkId
                WHERE Link_Members.MemberId = %s
                ORDER BY Links.LinkId DESC
                LIMIT 3"""
    val = (member_id,)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    result = cursor.fetchall()
    return result


def get_all_tags_on_member_and_count(member_id):
    cursor = db.cursor()
    sql = """SELECT TagName, Count(*) FROM Link_Tags
                INNER JOIN tags on tags.TagId = link_tags.TagId
                INNER JOIN link_members on link_members.LinkId = link_tags.LinkId
                WHERE link_members.MemberId = %s
                GROUP BY TagName
                ORDER BY TagName"""
    vals = (member_id,)
    cursor.execute(sql, vals)
    result = cursor.fetchall()
    cursor.close()
    return result


def add_link_members(link_id, member_id):
    cursor = db.cursor()
    sql = "INSERT INTO Link_Members(LinkId, MemberId) VALUES (%s, %s);"
    values = (link_id, member_id)
    cursor.execute(sql, values)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def add_user(discord_id, xp=0, contri=0):
    cursor = db.cursor()
    sql = "INSERT INTO Users(UserId, Xp, Cont) VALUES (%s, %s, %s);"
    values = (discord_id, xp, contri)
    cursor.execute(sql, values)
    db.commit()
    cursor.close()


def add_user_xp(discord_id, xp_to_add=1):
    cursor = db.cursor()
    sql = """UPDATE Users
                SET
                    Xp = Xp + %s
                WHERE
                    UserId = %s;
            """
    vals = (xp_to_add, discord_id)
    cursor.execute(sql, vals)
    db.commit()
    cursor.close()


def find_user(discord_id):
    cursor = db.cursor()
    sql = "SELECT UserId, Xp, Cont FROM Users WHERE UserId = %s;"
    val = (discord_id,)
    cursor.execute(sql, val)
    user = cursor.fetchone()[0]
    cursor.close()
    return user


def add_user_contribution(discord_id, contribution=1):
    cursor = db.cursor()
    sql = """UPDATE Users
                SET
                    Cont = Cont + %s
                WHERE
                    UserId = %s"""
    vals = (contribution, discord_id)
    cursor.execute(sql, vals)
    db.commit()
    cursor.close()


# def remove_user(discord_id):
#     cursor = db.cursor()
#     # sql = """UPDATE Users
#     #             SET
#     #                 Users.IsDeleted = 1
#     #             WHERE
#     #                 Users.UserId = %s;"""
#     value = (discord_id,)
#     cursor.execute(sql, value)
#     rowcount = cursor.rowcount
#     db.commit()
#     cursor.close()
#     return rowcount > 0


def get_leaderboard(number_of_users=10):
    cursor = db.cursor()
    sql = "SELECT UserId, Cont FROM Users ORDER BY Cont DESC LIMIT %s;"
    val = (number_of_users,)
    cursor.execute(sql, val)
    leaderboard = cursor.fetchall()
    cursor.close()
    return leaderboard


def add_moderator(discord_id):
    cursor = db.cursor()
    sql = "INSERT INTO Moderators(UserId) VALUES (%s);"
    value = (discord_id,)
    try:
        cursor.execute(sql, value)
    except mysql.connector.errors.IntegrityError:
        return None
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_moderator(discord_id):
    cursor = db.cursor()
    # sql = """UPDATE Moderators
    #             SET
    #                 Moderators.IsDeleted = 1
    #             WHERE
    #                 Moderators.UserId = %s;"""
    sql = "DELETE FROM Moderators WHERE UserId = %s"
    value = (discord_id,)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_moderator(discord_id):
    cursor = db.cursor()
    sql = "SELECT UserId FROM Moderators WHERE UserId = %s"
    val = (discord_id,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    cursor.close()
    return result


def add_channel(discord_id):
    cursor = db.cursor()
    sql = "INSERT INTO Channels(Channel) VALUES (%s);"
    value = (discord_id,)
    try:
        cursor.execute(sql, value)
    except mysql.connector.errors.IntegrityError:
        return
    db.commit()
    cursor.close()


def remove_channel(discord_id):
    cursor = db.cursor()
    sql = """DELETE channels, auditing_channels, reddit_channels
                FROM channels
                INNER JOIN auditing_channels 
                    ON channels.ChannelId = auditing_channels.ChannelId
                INNER JOIN reddit_channels 
                    ON channels.ChannelId = reddit_channels.ChannelId
                WHERE channels.ChannelId = %s;"""
    value = (discord_id,)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_channel(discord_id):
    cursor = db.cursor()
    sql = "SELECT ChannelId FROM Channels WHERE Channel = %s;"
    val = (discord_id,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    cursor.close()
    return result


def add_auditing_channel(discord_id):
    cursor = db.cursor()
    sql = """INSERT INTO Auditing_Channels(ChannelId)
            SELECT ChannelId FROM Channels 
            WHERE Channels.Channel = %s"""
    value = (discord_id,)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_auditing_channel(discord_id):
    cursor = db.cursor()
    # sql = """UPDATE Auditing_Channels
    #             SET
    #                 Auditing_Channels.IsDeleted = 1
    #             WHERE
    #                 Auditing_Channels.ChannelId = %s"""
    # sql = """DELETE FROM auditing_channels
    #             WHERE ChannelId = %s"""
    sql = """DELETE FROM auditing_channels
                WHERE ChannelId = ANY(
                SELECT ChannelId FROM Channels
                WHERE Channel = %s);"""
    value = (discord_id,)
    try:
        cursor.execute(sql, value)
    except Exception as e:
        print(e)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_auditing_channel(channel_id):
    cursor = db.cursor()
    sql = "SELECT ChannelId FROM Auditing_Channels WHERE ChannelId = %s"
    val = (channel_id,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    cursor.close()
    return result


def get_auditing_channels():
    cursor = db.cursor()
    sql = """select Channel from channels 
             left join auditing_channels 
             on auditing_channels.ChannelId = channels.ChannelId"""
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def add_reddit(reddit_name):
    cursor = db.cursor()
    sql = "INSERT INTO Reddit(RedditName) VALUES (%s);"
    value = (reddit_name,)
    try:
        cursor.execute(sql, value)
    except Exception as e:
        print(e)
        return
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


# def remove_reddit(reddit_name):
#     cursor = db.cursor()
#     sql = """UPDATE Reddit
#                 SET
#                     Reddit.IsDeleted
#                 WHERE
#                     Reddit.RedditName = %s;"""
#     value = (reddit_name,)
#     cursor.execute(sql, value)
#     rowcount = cursor.rowcount
#     db.commit()
#     cursor.close()
#     return rowcount > 0


def get_subreddit_id(reddit_name):
    cursor = db.cursor()
    sql = """SELECT RedditId FROM Reddit
                WHERE RedditName = %s"""
    val = (reddit_name,)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    result = cursor.fetchone()
    cursor.close()
    return result


def add_reddit_channel(channel_id, reddit_id):
    cursor = db.cursor()
    sql = "INSERT INTO Reddit_Channels(ChannelId, RedditId) VALUES (%s, %s);"
    values = (channel_id, reddit_id)
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(e)
        return
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_channel_from_subreddit(channel_id, subreddit_name):
    cursor = db.cursor()
    sql = """DELETE FROM Reddit_Channels
                WHERE RedditId = %s
                AND ChannelId = %s"""
    vals = (subreddit_name, channel_id)
    try:
        cursor.execute(sql, vals)
    except Exception as e:
        print(e)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


# def remove_reddit_channel(channel_id, reddit_id):
#     cursor = db.cursor()
#     sql = """UPDATE Reddit_Channels
#                 SET
#                     Reddit_Channels.IsDeleted = 1
#                 WHERE
#                     Reddit_Channels.ChannelId = %s
#                     AND
#                     Reddit_Channels.RedditId = %s;"""
#     values = (channel_id, reddit_id)
#     cursor.execute(sql, values)
#     rowcount = cursor.rowcount
#     db.commit()
#     cursor.close()
#     return rowcount > 0


def get_all_reddit_channels():
    cursor = db.cursor()
    sql = """select Channel from channels 
                inner join reddit_channels on channels.ChannelId = reddit_channels.ChannelId"""
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all_subreddits():
    cursor = db.cursor()
    sql = """select RedditName from reddit"""
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_channels_with_sub(reddit_name):
    cursor = db.cursor()
    sql = """select channel from channels
                inner join reddit on reddit.RedditName = %s
                inner join reddit_channels on reddit_channels.RedditId = reddit.RedditId
                where channels.ChannelId = reddit_channels.ChannelId"""
    val = (reddit_name,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


def random_link_from_links():
    cursor = db.cursor()
    sql = """SELECT Link, members.RomanName, groupz.RomanName FROM Links
                INNER JOIN link_members ON link_members.LinkId = Links.LinkId
                INNER JOIN members ON members.MemberId = link_members.MemberId
                INNER JOIN groupz ON groupz.GroupId = members.GroupId
                ORDER BY RAND()
                LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    return result

# def get_all_links_from_group(group_name):
#     cursor = db.cursor()
#     sql = """"""
#     val = (group_name,)
#     cursor.execute(sql, val)
#     result = cursor.fetchall()
#     cursor.close()
#     return result
