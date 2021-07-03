from discord import Embed
from discord import Color

# File for keeping embeds that are used frequently


def success_embed(message):
    embed = Embed(title='Success!',
                  description=message,
                  color=Color.green())
    return embed


def error_embed(message):
    embed = Embed(title='Error!',
                  description=message,
                  color=Color.red())
    return embed


def warning_embed(message):
    embed = Embed(title='Warning!',
                  description=message,
                  color=Color.orange())
    return embed


def permission_denied_embed():
    return error_embed('Permission Denied!')
