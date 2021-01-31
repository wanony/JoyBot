import json

with open('directories.json') as direc:
    direc_dict = json.load(direc)
with open(direc_dict["apis"], 'r') as apis:
    apis_dict = json.load(apis)

command_prefix = apis_dict["command_prefix"]

with open(direc_dict["custom"], 'r') as cust:
    custom_dict = json.load(cust)
with open(direc_dict["gfys"], 'r') as gfys:
    gfys_dict = json.load(gfys)
with open(direc_dict["levels"], 'r') as usrs:
    users = json.load(usrs)
with open(direc_dict["recents"], 'r') as rece:
    recent_dict = json.load(rece)
with open(direc_dict["contri"], 'r') as cont:
    contri_dict = json.load(cont)
with open(direc_dict["reddit"], 'r') as redd:
    reddit_dict = json.load(redd)
with open(direc_dict["twitch"], 'r') as twit:
    twitch_dict = json.load(twit)
