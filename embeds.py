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


def banned_word_embed(guild, word):
    message = f'Your message was deleted in {guild.name} because it contained the banned word {word}.'
    embed = Embed(title='Message Deleted!',
                  description=message,
                  color=Color.orange())
    embed.set_thumbnail(url=guild.icon)
    return embed


def permission_denied_embed():
    return error_embed('Permission Denied!')
