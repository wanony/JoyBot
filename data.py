import json
import mysql.connector as conn
import mysql.connector.errors
import threading
import datetime
import os

with open('directories.json') as direc:
    direc_dict = json.load(direc)
with open(direc_dict["apis"], 'r') as apis:
    apis_dict = json.load(apis)

default_prefix = apis_dict["command_prefix"]

with open(direc_dict["mods"], 'r') as mods:
    mods_dict = json.load(mods)


def check_user_is_mod(ctx):
    return find_moderator(ctx.author.id)


def check_user_is_owner(ctx):
    if ctx.author.id in mods_dict["owners"]:
        return True
    else:
        return False


def check_user_is_restricted(ctx):
    restricted = find_restricted_user_db(ctx.author.id)
    if restricted:
        return True
    else:
        return False


database = 'botdatabase'
username = apis_dict["database_user"]
password = apis_dict["database_password"]

db = conn.connect(
    host='localhost',
    user=username,
    passwd=password,
    database=database,
    buffered=True
)

# --- MAKE DATABASE BACKUP ON DAY CYCLES --- #


def backup_database():
    today = datetime.date.today()
    os.system(f'sudo mysqldump -u root botdatabase > ./backupgfys/backup-file-{today}.sql')
    print(f"Database backed up on {today} at {datetime.datetime.now()}")
    threading.Timer(86400.0, backup_database).start()


backup_database()

# --- CUSTOM COMMANDS --- #


def add_command(name, link, added_by):
    """Add a new custom command to the database."""
    cursor = db.cursor()
    sql = "INSERT INTO custom_commands(CommandName, Command, AddedBy) VALUES (%s, %s, %s);"
    val = (name, link, added_by)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def get_commands():
    """Returns a dictionary of all commands in the database."""
    cursor = db.cursor()
    sql = "SELECT CommandName, Command FROM custom_commands ORDER BY CommandName;"
    cursor.execute(sql)
    result = dict(cursor.fetchall())
    cursor.close()
    return result


def find_command(command_name):
    """Finds a specific command by name in the database."""
    cursor = db.cursor()
    sql = """SELECT CommandName FROM custom_commands
                WHERE CommandName = %s"""
    val = command_name
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def remove_command(name):
    """Removes a command by name from the database."""
    cursor = db.cursor()
    # sql = """UPDATE Custom_Commands
    #         SET
    #             Custom_Commands.IsDeleted = 1
    #         WHERE
    #             Custom_Commands.CommandName = %s;"""
    sql = """DELETE FROM custom_commands
                WHERE CommandName = %s"""
    value = (name,)
    cursor.execute(sql, value)
    db.commit()
    row_count = cursor.rowcount
    cursor.close()
    return row_count > 0


# --- LINK COMMANDS --- #


def add_link(link, added_by):
    """Adds a link to the database."""
    cursor = db.cursor()
    sql = "INSERT INTO links(Link, AddedBy) VALUES (%s, %s);"
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
    """Returns a count of all links, groups, and members."""
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
    """Returns a links unique ID in the database."""
    cursor = db.cursor()
    sql = "SELECT LinkId FROM links WHERE Link = %s"
    val = (link,)
    cursor.execute(sql, val)
    link_id = cursor.fetchone()[0]
    cursor.close()
    return link_id


def remove_link(group, member, link):
    """Removes a link from a member."""
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
    sql = """delete links FROM links
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
             WHERE links.Link = %s
             and links.LinkId = link_members.LinkId;"""
    value = (group, member, link)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def add_link_to_member(member_id, link_id):
    cursor = db.cursor()
    sql = """INSERT INTO link_members(LinkId, MemberId) VALUES (%s, %s);"""
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
    """Adds a new tag to the database."""
    cursor = db.cursor()
    sql = "INSERT INTO tags(TagName, AddedBy) VALUES (%s, %s);"
    value = (tag_name, added_by)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def add_tag_alias(tag_id, alias, added_by):
    cursor = db.cursor()
    sql = "INSERT INTO tag_aliases(TagId, Alias, AddedBy) VALUES (%s, %s, %s);"
    values = (tag_id, alias, added_by)
    cursor.execute(sql, values)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def get_all_tag_names():
    """Returns all tag names."""
    cursor = db.cursor()
    sql = "SELECT Alias FROM tag_aliases ORDER BY Alias"
    # sql = """SELECT Alias FROM Tag_Aliases ORDER BY Alias"""
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_tag_parent_from_alias(tag):
    """gets parent tag name"""
    cursor = db.cursor()
    sql = """SELECT TagName, tags.TagId FROM tags
             LEFT JOIN tag_aliases ON tags.TagId = tag_aliases.TagId
             WHERE tag_aliases.Alias = %s"""
    try:
        cursor.execute(sql, (tag,))
    except Exception as e:
        print(e)
    result = cursor.fetchone()
    cursor.close()
    return result


def get_all_alias_of_tag(tag_id):
    """Returns all aliases of tag from db."""
    cursor = db.cursor()
    sql = """select alias from tag_aliases
             left join tags
             on tags.TagId = tag_aliases.TagId
             where tag_aliases.TagId = %s"""
    val = (tag_id,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


def add_tag_alias_db(tag, alias, user_id):
    """Adds a new alias to an existing tag."""
    cursor = db.cursor()
    sql = """INSERT INTO tag_aliases(TagId, Alias, AddedBy)
             VALUES ((SELECT TagId FROM tags WHERE TagName = %s), %s, %s)"""
    val = (tag, alias, user_id)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def remove_tag_alias_db(tag, alias):
    """Adds a new alias to an existing tag."""
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
    """Returns the unique ID of a tag by name."""
    cursor = db.cursor()
    sql = "SELECT TagId FROM tags WHERE TagName = %s"
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
    """Returns a dict of tagnames and IDs that are on a link."""
    cursor = db.cursor()
    sql = """SELECT TagName, TagId, links.LinkId
             FROM tags, links
                WHERE
                    links.Link = %s
                    AND
                    tags.LinkId = links.LinkId;"""
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
    sql = """INSERT INTO link_tags(LinkId, TagId) SELECT links.LinkId, tags.TagId FROM links
             LEFT JOIN tag_aliases ON tag_aliases.Alias = %s
             LEFT JOIN tags ON tags.TagId = tag_aliases.TagId
             WHERE links.Link = %s"""
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
    sql = """DELETE FROM link_tags
          WHERE LinkId = ANY(SELECT LinkId FROM links WHERE Link = %s) 
          AND TagId = ANY(SELECT TagId FROM tags WHERE TagName = %s)"""
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
                inner join tag_aliases on tags.TagId = tag_aliases.TagId
                where tag_aliases.Alias = %s;"""
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
    sql = "INSERT INTO groupz(RomanName, AddedBy) VALUES (%s, %s);"
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
    sql = """SELECT groupz.GroupId FROM groupz
                left join groupz_aliases
                    on groupz_aliases.Alias = %s
                where groupz.GroupId = groupz_aliases.GroupId;"""
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
    sql = """SELECT groupz.GroupId, groupz.RomanName FROM groupz
                left join groupz_aliases
                    on groupz_aliases.Alias = %s
                where groupz.GroupId = groupz_aliases.GroupId;"""
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
    sql = """SELECT RomanName FROM groupz
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
    sql = "select Alias from groupz_aliases WHERE GroupId = %s"
    val = (group_name,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


# --- Members Commands --- #


def add_member(group_name, member_name, addedby):
    cursor = db.cursor()
    sql = """INSERT INTO members(GroupId, RomanName, AddedBy)
                VALUES ((SELECT groupz.GroupId FROM groupz WHERE groupz.RomanName = %s),
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
    sql = "DELETE FROM members WHERE RomanName = %s AND GroupId = %s"
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
    sql = """SELECT members.MemberId FROM members
                left join member_aliases
                    on member_aliases.MemberId = members.MemberId
                WHERE alias = %s AND members.GroupId = %s"""
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
    sql = """SELECT members.MemberId, members.RomanName FROM members
                left join member_aliases
                    on member_aliases.MemberId = members.MemberId
                WHERE alias = %s AND members.GroupId = %s"""
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
    """Returns a dict of members of a group."""
    cursor = db.cursor()
    sql = """SELECT members.RomanName FROM members
                INNER JOIN groupz ON groupz.RomanName = %s
                WHERE members.GroupId = groupz.GroupId;"""
    val = (group_name,)
    cursor.execute(sql, val)
    members = cursor.fetchall()
    cursor.close()
    return members


def get_members_of_group_by_group_id(group_id):
    cursor = db.cursor()
    sql = """SELECT members.RomanName FROM members
                INNER JOIN groupz ON groupz.GroupId = %s
                WHERE members.GroupId = groupz.GroupId;"""
    val = group_id
    cursor.execute(sql, val)
    members = cursor.fetchall()
    cursor.close()
    return members


def get_member_links(member_id):
    cursor = db.cursor()
    sql = """select Link from links
                inner join link_members 
                on links.LinkId = link_members.LinkId
                where link_members.MemberId = %s;"""
    vals = (member_id,)
    try:
        cursor.execute(sql, vals)
    except Exception as e:
        print(e)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_members_of_group_and_link_count(group_id):
    cursor = db.cursor()
    sql = """SELECT members.RomanName,
                (SELECT COUNT(*) FROM link_members WHERE link_members.MemberId = members.MemberId)
                FROM members
                INNER JOIN groupz ON groupz.GroupId = %s
                WHERE members.GroupId = groupz.GroupId
                ORDER BY members.RomanName"""
    val = (group_id,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_member_links_with_tag(member_id, tag):
    cursor = db.cursor()
    sql = """select Link from links
             left join link_members 
                on links.LinkId = link_members.LinkId
            left join link_tags 
                on link_tags.LinkId = links.LinkId 
            left join tags 
                on tags.TagId = link_tags.TagId
            left join tag_aliases
                on tag_aliases.TagId = tags.TagId
            WHERE tag_aliases.Alias = %s
            AND link_members.MemberId = %s
            """
    vals = (tag, member_id)
    try:
        cursor.execute(sql, vals)
    except Exception as e:
        print(e)
    result = cursor.fetchall()
    cursor.close()
    return result


def count_links_of_member(member_id):
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM link_members WHERE MemberId = (%s)"
    val = (member_id,)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    result = cursor.fetchone()[0]
    return result


def last_three_links(member_id):
    cursor = db.cursor()
    sql = """SELECT Link FROM links
                INNER JOIN link_members ON links.LinkId = link_members.LinkId
                WHERE link_members.MemberId = %s
                ORDER BY links.LinkId DESC
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
    sql = """SELECT TagName, Count(*) FROM link_tags
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
    sql = "INSERT INTO link_members(LinkId, MemberId) VALUES (%s, %s);"
    values = (link_id, member_id)
    cursor.execute(sql, values)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def add_user(discord_id, xp=0, contri=0):
    cursor = db.cursor()
    sql = "INSERT INTO users(UserId, Xp, Cont) VALUES (%s, %s, %s);"
    values = (discord_id, xp, contri)
    cursor.execute(sql, values)
    db.commit()
    cursor.close()


def add_user_xp(discord_id, xp_to_add=1):
    cursor = db.cursor()
    sql = """UPDATE users
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
    sql = "SELECT UserId, Xp, Cont FROM users WHERE UserId = %s;"
    val = (discord_id,)
    cursor.execute(sql, val)
    user = cursor.fetchone()
    cursor.close()
    return user


def add_user_contribution(discord_id, contribution=1):
    cursor = db.cursor()
    sql = """UPDATE users
                SET
                    Cont = Cont + %s
                WHERE
                    UserId = %s"""
    vals = (contribution, discord_id)
    cursor.execute(sql, vals)
    db.commit()
    cursor.close()


def add_cont_from_one_user_to_other(from_id, to_id):
    cursor = db.cursor()
    sql = """UPDATE users as U, users AS OldUser
             SET U.Cont = U.Cont + OldUser.Cont
             WHERE U.UserId = %s AND OldUser.UserId = %s"""
    val = (to_id, from_id)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
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
    sql = "SELECT UserId, Cont FROM users ORDER BY Cont DESC LIMIT %s;"
    val = (number_of_users,)
    cursor.execute(sql, val)
    leaderboard = cursor.fetchall()
    cursor.close()
    return leaderboard


def get_idol_leaderboard(number_of_entries=10):
    cursor = db.cursor()
    sql = """SELECT members.RomanName, groupz.RomanName, COUNT(*) FROM link_members
             JOIN members ON members.MemberId = link_members.MemberId
             JOIN groupz ON members.GroupId = groupz.GroupId
             GROUP BY members.MemberId
             ORDER BY COUNT(*) DESC
             LIMIT %s"""
    val = (number_of_entries,)
    cursor.execute(sql, val)
    leaderboard = cursor.fetchall()
    cursor.close()
    return leaderboard


def get_group_leaderboard(number_of_entries=10):
    cursor = db.cursor()
    sql = """SELECT groupz.RomanName, COUNT(*) FROM link_members
             JOIN members ON members.MemberId = link_members.MemberId
             JOIN groupz ON members.GroupId = groupz.GroupId
             GROUP BY groupz.GroupId
             ORDER BY count(*) DESC
             LIMIT %s"""
    val = (number_of_entries,)
    cursor.execute(sql, val)
    leaderboard = cursor.fetchall()
    cursor.close()
    return leaderboard


def add_moderator(discord_id):
    cursor = db.cursor()
    sql = "INSERT INTO moderators(UserId) VALUES (%s);"
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
    sql = "DELETE FROM moderators WHERE UserId = %s"
    value = (discord_id,)
    cursor.execute(sql, value)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_moderator(discord_id):
    cursor = db.cursor()
    sql = "SELECT UserId FROM moderators WHERE UserId = %s"
    val = (discord_id,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    cursor.close()
    return result


def add_channel(discord_id):
    cursor = db.cursor()
    sql = "INSERT INTO channels(Channel) VALUES (%s);"
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
    sql = "SELECT ChannelId FROM channels WHERE Channel = %s;"
    val = (discord_id,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    cursor.close()
    return result


def add_auditing_channel(discord_id):
    cursor = db.cursor()
    sql = """INSERT INTO auditing_channels(ChannelId)
            SELECT ChannelId FROM channels 
            WHERE channels.Channel = %s"""
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
                SELECT ChannelId FROM channels
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
    sql = "SELECT ChannelId FROM auditing_channels WHERE ChannelId = %s"
    val = (channel_id,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    cursor.close()
    return result


def get_auditing_channels():
    cursor = db.cursor()
    sql = """select channels.Channel from channels
             inner join auditing_channels
             on auditing_channels.ChannelId = channels.ChannelId"""
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def add_reddit(reddit_name):
    cursor = db.cursor()
    sql = "INSERT INTO reddit(RedditName) VALUES (%s);"
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
    sql = """SELECT RedditId FROM reddit
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
    sql = "INSERT INTO reddit_channels(ChannelId, RedditId) VALUES (%s, %s);"
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
    sql = """DELETE FROM reddit_channels
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
    sql = """SELECT Link, members.RomanName, groupz.RomanName FROM links
                INNER JOIN link_members ON link_members.LinkId = links.LinkId
                INNER JOIN members ON members.MemberId = link_members.MemberId
                INNER JOIN groupz ON groupz.GroupId = members.GroupId
                ORDER BY RAND()
                LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    return result


def add_guild_db(guild_id):
    cursor = db.cursor()
    sql = """INSERT INTO guilds(Guild, Prefix) VALUES(%s, %s)"""
    val = (guild_id, default_prefix)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(e)
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def get_prefix_db(guild_id):
    cursor = db.cursor()
    sql = """SELECT Prefix FROM guilds WHERE Guild = %s;"""
    val = (guild_id,)
    try:
        cursor.execute(sql, val)
    except Exception as e:
        print(f'get_prefix_db {e}')
    result = cursor.fetchone()
    cursor.close()
    return result


def set_guild_prefix_db(guild_id, prefix):
    cursor = db.cursor()
    sql = """UPDATE guilds
                SET
                    Prefix = %s
                WHERE
                    Guild = %s"""
    val = (prefix, guild_id,)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def get_banned_words(guild_id):
    cursor = db.cursor()
    sql = """SELECT Word FROM banned_words
             JOIN guild_banned_words ON banned_words.WordId = guild_banned_words.WordId
             JOIN guilds ON guilds.GuildId = guild_banned_words.GuildId
             WHERE guilds.Guild = %s"""
    val = (guild_id,)
    cursor.execute(sql, val)
    result = [x[0] for x in cursor.fetchall()]
    cursor.close()
    return result


def add_banned_word(guild_id, word):
    cursor = db.cursor()
    sql = """"""
    val = (guild_id, word)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    db.commit()
    cursor.close()
    return rowcount > 0


def find_restricted_user_db(guild_id, user_id):
    cursor = db.cursor()
    sql = """SELECT UserId FROM restricted_users
             JOIN guilds ON guilds.GuildId = restricted_users.GuildId
             WHERE guilds.Guild = %s AND UserId = %s"""
    val = (guild_id, user_id,)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def add_restricted_user(guild_id, user_id):
    cursor = db.cursor()
    sql = """INSERT INTO restricted_users(GuildId, UserId) VALUES ((
             SELECT GuildId FROM guilds WHERE Guild = %s), %s)"""
    val = (guild_id, user_id,)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0


def remove_restricted_user(guild_id, user_id):
    cursor = db.cursor()
    sql = """DELETE FROM restricted_users WHERE GuildId = ANY(SELECT GuildId FROM guilds WHERE Guild = %s)
             AND UserId = %s"""
    val = (guild_id, user_id,)
    cursor.execute(sql, val)
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount > 0

# def get_all_links_from_group(group_name):
#     cursor = db.cursor()
#     sql = """"""
#     val = (group_name,)
#     cursor.execute(sql, val)
#     result = cursor.fetchall()
#     cursor.close()
#     return result
