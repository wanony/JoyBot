import os
import json
import shutil

get_directories_path = 'directories.json'


if __name__ == "__main__":
    dir_path = get_directories_path
    f = os.path.exists(dir_path)
    if f:
        answer = input("directories.json exists, would you like to overwrite (y/n)? ")
        if (answer != "Y" and answer != "y"):
            exit(1)
    f = os.path.exists("jsons/")
    if f:
        answer = input("/jsons exists, would you like to overwrite (y/n)? ")
        if (answer != "Y" and answer != "y"):
            exit(1)
        shutil.rmtree("jsons/")
    os.mkdir("jsons/")
    data = {
        "apis" : "jsons/apis.json",
        "cache_variables" : "jsons/cache.json",
        "mods" : "jsons/mods.json",
        "insta_file_path" : "jsons/insta",
    }
    with open(dir_path, 'w') as out:
        json.dump(data, out)
    for (name, path) in data.items():
        try:
            file = open(path, "x")
        except OSError:
            print(f"{name} file already exists at {path}")
    discord_token = input("Please enter discord token: ")
    command_prefix = input("Please enter command prefix: ")
    data_base_name = input("Please enter database name: ")
    data_base_user = input("Please enter database user: ")
    data_base_pass = input("Please enter database password: ")
    api_data = {
        "discord_token" : discord_token,
        "command_prefix" : command_prefix,
        "database_name" : data_base_name,
        "database_user" : data_base_user,
        "database_password" : data_base_pass,
        "gfy_client_id" : "",
        "gfy_client_secret" : "",
        "twitter_key" : "",
        "twitter_secret" : "",
        "twitter_access_token" : "",
        "twitter_access_secret" : ""
    }
    with open(data["apis"], "w") as file:
        json.dump(api_data, file)
    with open(data["cache_variables"], "w") as file:
        json.dump({}, file)
    with open(data["mods"], "w") as file:
        json.dump({"mods" : [], "owners" : []}, file)
