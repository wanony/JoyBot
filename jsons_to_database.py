import mysql.connector.errors as errors
import mysql.connector as conn
import json


with open('directories.json') as direc:
    direc_dict = json.load(direc)
with open(direc_dict["apis"], 'r') as apis:
    apis_dict = json.load(apis)
with open(direc_dict["gfys"], 'r') as gfys:
    gfys_dict = json.load(gfys)
with open(direc_dict["contri"], 'r') as contri:
    contri_dict = json.load(contri)
with open(direc_dict["levels"], 'r') as usrs:
    users = json.load(usrs)
with open(direc_dict["auditing"], 'r') as aud:
    auditing_dict = json.load(aud)
with open(direc_dict["custom"], 'r') as cus:
    custom_dict = json.load(cus)
with open(direc_dict["reddit"], 'r') as redd:
    reddit_dict = json.load(redd)

db = conn.connect(
    host="localhost",
    user=apis_dict["database_user"],
    passwd=apis_dict["database_password"],
    database="botdatabase",
    auth_plugin='mysql_native_password'
)

cursor = db.cursor(buffered=True)
my_id = 107215130785243136


for user in users:
    if str(user) in contri_dict:
        usr_cont = contri_dict[str(user)]['cont']
    else:
        usr_cont = 0
    sql = "INSERT INTO users(UserId, Xp, Cont) VALUES (%s, %s, %s);"
    vals = (user, users[user]['xp'], usr_cont)
    cursor.execute(sql, vals)

for group in gfys_dict["groups"]:
    # add group to groupz table
    sql = "INSERT INTO groupz(RomanName, AddedBy) VALUES (%s, %s);"
    vals = (group, my_id)
    cursor.execute(sql, vals)
    # format group into string for query
    sel_sql = "SELECT GroupId FROM groupz WHERE RomanName = (%s);"
    cursor.execute(sel_sql, (group,))

    group_id = cursor.fetchone()[0]
    alias_sql = "INSERT INTO groupz_aliases(GroupId, Alias, AddedBy) VALUES (%s, %s, %s)"
    vals = (group_id, group, my_id)
    cursor.execute(alias_sql, vals)
    # iter to add members to members table
    for member in gfys_dict["groups"][group]:
        msql = """
             INSERT INTO members(GroupId, RomanName, AddedBy) VALUES (%s, %s, %s);
             """
        val = (group_id, member, my_id)
        cursor.execute(msql, val)
        # string for member name
        sel_sql = """SELECT MemberId FROM members
                        left JOIN groupz ON groupz.GroupId = members.GroupId
                        WHERE members.RomanName = %s
                        AND groupz.GroupId = %s"""
        cursor.execute(sel_sql, (member, group_id))

        memberid = cursor.fetchone()[0]
        alias_sql = "INSERT INTO member_aliases(MemberId, Alias, AddedBy) VALUES (%s, %s, %s)"
        vals = (memberid, member, my_id)
        try:
            cursor.execute(alias_sql, vals)
        except Exception as e:
            print(e)
        # add links to links table
        for link in gfys_dict["groups"][group][member]:
            if link.endswith("/"):
                link = link[:-1]
            if link.startswith("https://gfycat.com/"):
                split = link.split("/")
                if "-" in split[-1]:
                    split[-1] = split[-1].split("-")
                    split[-1] = split[-1][0]
                link = "https://gfycat.com/" + split[-1]
            lsql = "INSERT INTO links(Link, AddedBy) VALUES (%s, %s);"
            valz = (link, my_id)
            cursor.execute(lsql, valz)
            # MIGHT BE SOME ERROR HERE #############################################################
            lidsql = "SELECT * FROM links WHERE Link = (%s);"
            cursor.execute(lidsql, (link,))
            lid = cursor.fetchone()[0]
            # add to link_members table
            lmsql = "INSERT INTO link_members(LinkId, MemberId) VALUES (%s, %s);"
            try:
                cursor.execute(lmsql, (lid, memberid))
            except errors.IntegrityError as e:
                print(e)
                # sql = "DELETE FROM Links WHERE Link = (%s) LIMIT =1;"
                # cursor.execute(sql, (link,))


for tag in gfys_dict["tags"]:
    sql = "INSERT INTO tags(TagName, Addedby) VALUES (%s, %s);"
    get_tag_id = "SELECT TagId FROM tags WHERE TagName = (%s)"
    alias_sql = "INSERT INTO tag_aliases(TagId, Alias, AddedBy) VALUES (%s, %s, %s)"
    cursor.execute(sql, (tag, my_id))
    cursor.execute(get_tag_id, (tag,))
    t_id = cursor.fetchone()[0]
    cursor.execute(alias_sql, (t_id, tag, my_id))
    # add to links_tags table
    for link in gfys_dict["tags"][tag]:
        # MIGHT BE SOME ERROR HERE #############################################################
        if link.endswith("/"):
            link = link[:-1]
        if link.startswith("https://gfycat.com/"):
            split = link.split("/")
            if "-" in split[-1]:
                split[-1] = split[-1].split("-")
                split[-1] = split[-1][0]
            link = "https://gfycat.com/" + split[-1]
        jkl = "SELECT * FROM links WHERE Link = (%s);"
        cursor.execute(jkl, (link,))
        linkrow = cursor.fetchone()
        if linkrow is not None:
            l_id = linkrow[0]
        else:
            continue

        tkl = """SELECT * FROM tags
            WHERE TagName = (%s);"""
        cursor.execute(tkl, (tag,))
        t_id = cursor.fetchone()[0]
        ejif = "INSERT INTO link_tags(LinkId, TagId) VALUES (%s, %s);"
        values = (l_id, t_id)
        try:
            cursor.execute(ejif, values)
        except Exception as e:
            print(e)


channel_sql = "INSERT INTO channels(Channel) VALUES (%s);"
for reddit in reddit_dict:
    reddit_sql = "INSERT INTO reddit (RedditName) VALUES (%s);"
    cursor.execute(reddit_sql, (reddit,))
    channels = reddit_dict[reddit]["channels"]
    rsql = "INSERT INTO reddit_channels(ChannelId, RedditId) VALUES (%s, %s);"
    for channel in channels:
        try:
            cursor.execute(channel_sql, (channel,))
        except Exception as e:
            print(e)
        select_sql = "SELECT * FROM channels WHERE Channel = (%s);"
        cursor.execute(select_sql, (channel,))
        channel_id = cursor.fetchone()[0]
        select_red = "SELECT * FROM reddit WHERE RedditName = (%s);"
        cursor.execute(select_red, (reddit,))
        reddit_id = cursor.fetchone()[0]
        cursor.execute(rsql, (channel_id, reddit_id))


for channel in auditing_dict["auditing_channels"]:
    # check if channel exists
    isitthere = "SELECT * FROM channels WHERE Channel = (%s);"
    cursor.execute(isitthere, (channel,))
    if cursor.fetchone() is None:
        cursor.execute(channel_sql, (channel,))
        cursor.execute(isitthere, (channel,))
        c_id = cursor.fetchone()[0]
        s = "INSERT INTO auditing_channels(ChannelId) VALUES (%s);"
        cursor.execute(s, (c_id,))
    else:
        c_id = cursor.fetchone()[0]
        s = "INSERT INTO auditing_channels(ChannelId) VALUES (%s);"
        cursor.execute(s, (c_id,))


for command in custom_dict["commands"]:
    command_link = custom_dict["commands"][command]
    sql = "INSERT INTO custom_commands(CommandName, Command, AddedBy) VALUES (%s, %s, %s);"
    vals = (command, command_link, my_id)
    cursor.execute(sql, vals)


db.commit()
cursor.close()
db.close()
