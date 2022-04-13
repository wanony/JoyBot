import os

import nextcord as discord
from nextcord import SlashOption
from nextcord.ext import commands

from datetime import datetime

# import lots of methods
from data import add_channel, add_tag_alias_db, remove_tag_alias_db, add_group_alias_db, remove_group_alias_db, \
    add_cont_from_one_user_to_other, perma_user_db, remove_perma_user_db, delete_link_from_database, gfy_v2_test, \
    find_member_id, pick_groups, get_group_aliases, pick_group_members
from data import remove_member_alias_db, add_member_alias_db, add_tag, find_group_id, add_group, remove_group
from data import remove_moderator, add_moderator, get_members_of_group, add_member, remove_member, apis_dict
from data import remove_auditing_channel, add_auditing_channel, remove_command, remove_link, remove_tag_from_link
from data import remove_tag, check_user_is_mod, check_user_is_owner

from embeds import success_embed, error_embed, permission_denied_embed


def is_owner():
    def check_owner(ctx):
        x = check_user_is_owner(ctx)
        return True if x else False

    return commands.check(check_owner)


def is_mod():
    async def check_mod(ctx):
        x = check_user_is_mod(ctx)
        return True if x else False

    return commands.check(check_mod)


class Owner(commands.Cog):
    """Commands for the owner.
    """

    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient

    @commands.command(name='muc', aliases=['merge_user_cont', 'mergeusercont'])
    @is_owner()
    async def merge_user_contribution(self, ctx, member1: discord.Member, member2: discord.Member):
        """Add contribution from first arguement to second argument"""
        add_cont_from_one_user_to_other(member1.id, member2.id)
        ctx.send(embed=success_embed('Merged user contribution'))

    @commands.command(name='forcedelete', aliases=['forcedel', 'fdel'])
    @is_owner()
    async def force_delete_link(self, ctx, *links):
        delcounter = 0
        for link in links:
            removed = delete_link_from_database(link)
            if removed:
                delcounter += 1
            else:
                await ctx.send(f'failed to removed {link}')
        if delcounter > 0:
            await ctx.send(embed=success_embed(f'Removed {delcounter} link(s)!'))

    @commands.command()
    @is_owner()
    async def remove_moderator(self, ctx, member: discord.Member):
        """Add user to moderator list."""
        removed = remove_moderator(member.id)
        if removed:
            await ctx.send(embed=success_embed(f'{member} is no longer a moderator!'))
        else:
            await ctx.send(embed=error_embed(f'{member} is not a moderator!'))

    @commands.command()
    @is_owner()
    async def add_moderator(self, ctx, member: discord.Member):
        """Add user to moderator list."""
        added = add_moderator(member.id)
        if added:
            await ctx.send(embed=success_embed(f'{member} is now a moderator!'))
        else:
            await ctx.send(embed=error_embed(f'{member} is already a moderator!'))

    @commands.command()
    @is_owner()
    async def reload(self, ctx, cog_name=None):
        """Reload cog."""
        embed = discord.Embed(title='Reloading Results',
                              description='\uFEFF',
                              color=discord.Color.blurple())
        if cog_name is None:
            async with ctx.typing():
                reloaded = []
                failed = []
                for cog in os.listdir("./cogs"):
                    if cog.endswith(".py"):
                        try:
                            cog = f"cogs.{cog.replace('.py', '')}"
                            self.disclient.unload_extension(cog)
                            self.disclient.load_extension(cog)
                            reloaded.append(str(cog[5:]))
                        except commands.ExtensionNotLoaded:
                            failed.append(str(cog[5:]))
                if reloaded:
                    embed.add_field(name="Reloaded:",
                                    value=', '.join(reloaded))
                if failed:
                    embed.add_field(name="Failed to load:",
                                    value=', '.join(failed))
        else:
            async with ctx.typing():
                reloaded = []
                failed = []
                for cog in os.listdir("./cogs"):
                    if cog.endswith('.py'):
                        if cog[:-3] == cog_name:
                            cog = f"cogs.{cog.replace('.py', '')}"
                            try:
                                self.disclient.unload_extension(cog)
                                self.disclient.load_extension(cog)
                                reloaded.append(str(cog[5:]))
                            except commands.ExtensionNotLoaded:
                                failed.append(str(cog[5:]))
                if reloaded:
                    embed.add_field(name=f"Reloaded:",
                                    value=', '.join(reloaded))
                if failed:
                    embed.add_field(name=f"Failed to load:",
                                    value=', '.join(failed))
        await ctx.send(embed=embed)

    @commands.command()
    @is_owner()
    async def unload(self, ctx, cog_name):
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                if cog[:-3] == cog_name:
                    cog = f"cogs.{cog.replace('.py', '')}"
                    try:
                        self.disclient.unload_extension(cog)
                    except commands.ExtensionNotLoaded:
                        await ctx.send('Failed to unload cog.')
        await ctx.send('Unloaded cog!')

    @commands.command()
    @is_owner()
    async def load(self, ctx, cog_name):
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                if cog[:-3] == cog_name:
                    cog = f"cogs.{cog.replace('.py', '')}"
                    try:
                        self.disclient.load_extension(cog)
                    except commands.ExtensionNotLoaded:
                        await ctx.send('Failed to load cog.')
        await ctx.send('Loaded cog!')

    @commands.command()
    @is_owner()
    async def perma_user(self, ctx, user_id):
        """Stops user from added anything to the bot"""
        perma = perma_user_db(user_id)
        if perma:
            await ctx.send(embed=success_embed("User successfully perma'd."))
        else:
            await ctx.send(embed=error_embed("Failed to perma user."))

    @commands.command()
    @is_owner()
    async def remove_perma_user(self, ctx, user_id):
        """Removes user from perma ban"""
        unperma = remove_perma_user_db(user_id)
        if unperma:
            await ctx.send(embed=success_embed("User un-perma'd."))
        else:
            await ctx.send(embed=error_embed("Failed to un-perma user."))

    @commands.command()
    @is_owner()
    async def list_links(self, ctx, group, idol):
        links = gfy_v2_test(group, idol)
        num_of_links = len(links)
        embed = discord.Embed(
            title="List of Links",
            description=f"All {num_of_links} links of {links[0][2]}'s {links[0][3]}.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)
        for i, link in enumerate(links):
            await ctx.send(f"{i + 1}. {link[-1]}")

    @commands.command()
    @is_owner()
    async def link_duplicate_members(self, ctx, group_one, member_one, group_two, member_two):
        """Create a link between two members links, therefore allowing their links to seamlessly be accessed
        no matter what group they are referenced from. For example, if one idol is part of two different groups,
        we can link the link tables together to reference the same ID, in a sense creating an alias on top of the
        aliases they may already have."""
        # get member one's ID
        group_one_id = find_group_id(group_one)
        member_one_id = find_member_id(group_one_id, member_one)

        # get member two's ID
        group_two_id = find_group_id(group_two)
        member_two_id = find_member_id(group_two_id, member_two)

        # create the link entries again with the two sets of ID's
        pass

    @commands.command()
    @is_owner()
    async def unlink_duplicate_members(self, ctx, group_one, member_one, group_two, member_two):
        pass


class Moderation(commands.Cog):
    """Commands for Joy moderators.
    """

    def __init__(self, disclient):
        """Initialise client."""
        self.disclient = disclient

    @discord.slash_command(
        name="addgroup",
        description="add a new group to Joy"
    )
    @is_mod()
    async def add_group(self,
                        interaction: discord.Interaction,
                        group: str):
        """Adds a group"""
        group = group.lower()
        success = add_group(group, interaction.user.id)
        if success:
            add_group_alias_db(group, group, interaction.user.id)
            msg = f"Added group {group}!"
            await moderation_auditing(self.disclient, interaction.user, msg)
            await interaction.response.send_message(embed=success_embed(msg))
        else:
            msg = f"{group} already exists!"
            await interaction.response.send_message(embed=error_embed(msg))

    @discord.slash_command(
        name="addgroupalias",
        description="add an alias to a group"
    )
    @is_mod()
    async def add_group_alias(self,
                              interaction: discord.Interaction,
                              group: str = SlashOption(
                                  name="group",
                                  description="a group to add an alias to",
                                  required=True
                              ),
                              alias: str = SlashOption(
                                  name="alias",
                                  description="the alias to add to the group",
                                  required=True
                              )):
        """Adds an alias to an existing group that can then be used to
        reference the group in other commands. A list of aliases can be
        passed through in one command, but only one group.
        Example: .add_group_alias redvelvet rv
        Example: .add_group_alias <group> <alias1> <alias2>"""
        group = group.lower()
        alias = alias.lower()
        added = add_group_alias_db(group, alias, interaction.user.id)
        if added:
            act = f"Added alias {alias} to {group}!"
            await moderation_auditing(self.disclient, interaction.user, act)
            await interaction.response.send_message(embed=success_embed(act))
        else:
            msg = f"Skipped adding duplicate alias {alias}!"
            await interaction.response.send_message(embed=error_embed(msg))

    @discord.slash_command(
        name="deletegroupalias",
        description="delete group alias"
    )
    @is_mod()
    async def delete_group_alias(self,
                                 interaction: discord.Interaction,
                                 group: str = SlashOption(
                                     name="group",
                                     description="group to delete alias from",
                                     required=True
                                 ),
                                 alias: str = SlashOption(
                                     name="alias",
                                     description="alias to delete from group",
                                     required=True
                                 )):
        """Removes an alias from an existing group.
        A list of aliases can be passed through in one command, but only one group.
        Example: .remove_group_alias redvelvet rv
        Example: .remove_group_alias <group> <alias1> <alias2>"""
        group = group.lower()
        alias = alias.lower()
        removed = remove_group_alias_db(group, alias)
        if removed:
            act = f"Removed alias {alias} from {group}!"
            await moderation_auditing(self.disclient, interaction.user, act)
            await interaction.response.send_message(embed=success_embed(act))
        else:
            msg = f"Failed to remove alias {alias} from {group}!"
            await interaction.response.send_message(embed=error_embed(msg))

    @discord.slash_command(
        name="addidol",
        description="add an idol to a group!"
    )
    @is_mod()
    async def add_idols(self,
                        interaction: discord.Interaction,
                        group: str = SlashOption(
                            name="group",
                            description="the group to add to",
                            required=True
                        ),
                        idol: str = SlashOption(
                            name="idol",
                            description="the idol to add to the group",
                            required=True
                        )):
        """Adds an idol to an already existing group"""
        group = group.lower()
        idol = idol.lower()
        members = get_members_of_group(group)
        members = [x[0] for x in members]
        if idol in members:
            msg = f"{idol} already added to {group}!"
            await interaction.response.send_message(embed=error_embed(msg))
            return

        added = add_member(group, idol, interaction.user.id)
        if added:
            add_member_alias_db(group, idol, idol, interaction.user.id)
            act = f"Added idol: {idol} to {group}!"
            await moderation_auditing(self.disclient, interaction.user, act)
            await interaction.response.send_message(embed=success_embed(act))
        else:
            msg = f"Failed to add {idol} to {group}!"
            await interaction.response.send_message(embed=error_embed(msg))

    @discord.slash_command(
        name="addidolalias",
        description="add an alias to an idol"
    )
    @is_mod()
    async def add_idol_alias(self,
                             interaction: discord.Interaction,
                             group: str = SlashOption(
                                 name="group",
                                 description="group of the idol",
                                 required=True
                             ),
                             idol: str = SlashOption(
                                 name="idol",
                                 description="idol to add alias to",
                                 required=True
                             ),
                             alias: str = SlashOption(
                                 name="alias",
                                 description="alias to add to idol",
                                 required=True
                             )):
        """Adds an alias to an idol.
        A list of aliases can be passed through in one command, but only one idol.
        Please ensure you use the members name, and not an alias for the second argument.
        Example: .add_idol_alias redvelvet joy j
        Example: .add_idol_alias <group> <idol> <alias1> <alias2>"""
        group = group.lower()
        idol = idol.lower()
        alias = alias.lower()
        added = add_member_alias_db(group, idol, alias, interaction.user.id)
        if added:
            act = f"Added alias: {alias} to {idol}!"
            await moderation_auditing(self.disclient, interaction.user, act)
            await interaction.response.send_message(embed=success_embed(act))
        else:
            msg = f"Failed to add alias {alias} to {idol}!"
            await interaction.response.send_message(embed=error_embed(msg))

    @discord.slash_command(
        name="deleteidolalias",
        description="remove alias from an idol"
    )
    @is_mod()
    async def delete_idol_alias(self,
                                interaction: discord.Interaction,
                                group: str = SlashOption(
                                    name="group",
                                    description="group of the idol",
                                    required=True
                                ),
                                idol: str = SlashOption(
                                    name="idol",
                                    description="idol to add alias to",
                                    required=True
                                ),
                                alias: str = SlashOption(
                                    name="alias",
                                    description="alias to add to idol",
                                    required=True
                                )):
        """Removes an alias from an idol.
        A list of aliases can be passed through in one command, but only one idol.
        Please ensure you use the members name, and not an alias for the second argument.
        Example: .remove_idol_alias redvelvet joy j
        Example: .remove_idol_alias <group> <idol> <alias1> <alias2>"""
        group = group.lower()
        idol = idol.lower()
        alias = alias.lower()
        removed = remove_member_alias_db(group, idol, alias)
        if removed:
            act = f"Removed alias: {alias} from {idol}!"
            await moderation_auditing(self.disclient, interaction.user, act)
            await interaction.response.send_message(embed=success_embed(act))
        else:
            msg = f"""Failed to remove alias {alias} from {idol}!
                   \nPlease make sure you do not use an alias for the idol slash option!."""
            await interaction.response.send_message(embed=error_embed(msg))

    @commands.command(aliases=['removetag', 'removetagfromlink, remove_tag_from_link'])
    @is_mod()
    async def remove_tag(self, ctx, link, *tags):
        """
        Removes tag(s) from a link previously added
        Example: <link> <tag> <tag> <tag>
        Any number of tags can be removed in one command.
        """
        tags_list = tags
        # rework lists to strings once working
        removed = []
        not_there = []
        for tag in tags_list:
            tag = tag.lower()
            remove = remove_tag_from_link(link, tag)
            if remove:
                removed.append(tag)
            else:
                not_there.append(tag)
        if removed and not_there:
            r = ', '.join(removed)
            nt = ', '.join(not_there)
            act = f"Removed tag(s): {r} from {link}"
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(f'Removed {r} tag(s) from link!\nLink did not have: {nt}'))
        elif removed:
            r = ', '.join(removed)
            act = f"Removed tag(s): {r} from the link:\n{link}"
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(f'Removed {r} tag(s) from link!'))
        else:
            nt = ', '.join(not_there)
            await ctx.send(embed=error_embed(f'Link did not have tag(s): {nt}!'))

    @commands.command(aliases=['createtag'])
    @is_mod()
    async def create_tag(self, ctx, tag):
        """Adds a new tag, which will be available for use."""
        if not check_user_is_mod(ctx):
            await ctx.send(embed=permission_denied_embed())
            return

        tag = tag.lower()
        added = add_tag(tag, ctx.author.id)
        add_tag_alias_db(tag, tag, ctx.author.id)
        if added:
            act = f'Added tag: {tag}!'
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(act))
        else:
            await ctx.send(embed=error_embed(f'{tag} already exists!'))

    @commands.command(aliases=['deletetag', 'deltag'])
    @is_mod()
    async def delete_tag(self, ctx, tag):
        """Completely deletes a tag.
        All links with this tag, will no longer have this tag."""
        tag = tag.lower()
        removed = remove_tag(tag)
        if removed:
            act = f'Deleted tag: {tag}!'
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(act))
        else:
            await ctx.send(embed=error_embed(f'{tag} does not exist!'))

    @commands.command(aliases=['addtagalias'])
    @is_mod()
    async def add_tag_alias(self, ctx, tag, *aliases):
        """Adds an alias to a tag.
        A list of aliases can be passed through in one command, but only one tag.
        Please ensure you use the tag name, and not an alias for the first argument.
        Example: .add_tag_alias <tag> <alias>
        Example: .add_tag_alias <tag> <alias1> <alias2>"""
        tag = tag.lower()
        added_aliases = []
        invalid_aliases = []
        for alias in aliases:
            alias = alias.lower()
            added = add_tag_alias_db(tag, alias, ctx.author.id)
            if added:
                added_aliases.append(alias)
            else:
                invalid_aliases.append(alias)
        if invalid_aliases and added_aliases:
            exists = ', '.join(invalid_aliases)
            add = ', '.join(added_aliases)
            act = f"Added alias(es): {add} to {tag}!"
            await moderation_auditing(self.disclient, ctx.author, act)
            msg = f"Added alias(es): {add} to {tag}!\nSkipped adding duplicates: {exists}!"
            await ctx.send(embed=success_embed(msg))
        elif added_aliases and not invalid_aliases:
            msg = f"Added aliases(s): {', '.join(added_aliases)} to {tag}!"
            await moderation_auditing(self.disclient, ctx.author, msg)
            await ctx.send(embed=success_embed(msg))
        else:
            msg = f"Skipped adding duplicate alias(es): {', '.join(invalid_aliases)}!"
            await ctx.send(embed=error_embed(msg))

    @commands.command(aliases=['deltagalias', 'removetagalias', 'dta'])
    @is_mod()
    async def delete_tag_alias(self, ctx, tag, *aliases):
        """Removes an alias from a tag.
        A list of aliases can be passed through in one command, but only one tag.
        Please ensure you use the tag name, and not an alias for the first argument.
        Example: .delete_tag_alias <tag> <alias>
        Example: .delete_tag_alias <tag> <alias1> <alias2>"""
        tag = tag.lower()
        removed_aliases = []
        invalid_aliases = []
        for alias in aliases:
            alias = alias.lower()
            removed = remove_tag_alias_db(tag, alias)
            if removed:
                removed_aliases.append(alias)
            else:
                invalid_aliases.append(alias)
        if invalid_aliases and removed_aliases:
            exists = ', '.join(invalid_aliases)
            rem = ', '.join(removed_aliases)
            act = f"Removed alias(es): {rem} from {tag}!"
            await moderation_auditing(self.disclient, ctx.author, act)
            msg = f"Removed alias(es): {rem} from {tag}!\nFailed to removed: {exists}!"
            await ctx.send(embed=success_embed(msg))
        elif removed_aliases and not invalid_aliases:
            msg = f"Removed aliases(s): {', '.join(removed_aliases)} from {tag}!"
            await moderation_auditing(self.disclient, ctx.author, msg)
            await ctx.send(embed=success_embed(msg))
        else:
            msg = f"Failed to remove alias(es): {', '.join(invalid_aliases)} from {tag}!"
            await ctx.send(embed=error_embed(msg))

    @commands.command(aliases=[
        'delfancam', 'delete_fancam', 'delete_image', 'delimage', 'delete_gfy', 'delgfy', 'del', 'dellink'
    ])
    @is_mod()
    async def delete_link(self, ctx, group, idol, *links):
        """
        Deletes link(s) from an idol.
        Example: .delete_link <group> <idol> <link> <link> <link>
        """
        link_list = links
        group = group.lower()
        idol = idol.lower()
        # change list to string later
        failed = []
        success = []
        for link in link_list:
            if '-' in link:
                link = link.split('-')[0]
            removed = remove_link(group, idol, link)
            if removed:
                success.append(link)
            else:
                failed.append(link)
        if failed and not success:
            f = ', '.join(failed)
            await ctx.send(embed=error_embed(f'Failed to delete: {f}'))
        elif len(success) > 0 and failed:
            f = ', '.join(failed)
            s = '\n' + '\n'.join(success)
            act = f'Deleted link(s) from {group} {idol}: {s}'
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(f'Removed {len(success)} links!\nFailed to delete: {f}'))
        else:
            s = '\n' + '\n'.join(success)
            act = f'Deleted link(s) from {group} {idol}: {s}'
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(f'Removed {len(success)} links!'))

    @commands.command(aliases=['delgroup', 'deletegroup'])
    @is_mod()
    async def delete_group(self, ctx, group):
        """
        Deletes an entire group and all idols within
        Example: .delete_group <group>
        """
        group = group.lower()
        removed = remove_group(group)
        if removed:
            act = f"Deleted group: {group}"
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(f'Removed {group}'))
        else:
            await ctx.send(embed=error_embed(f'No group added called {group}!'))

    @commands.command(aliases=['delidol', 'delidols', 'deleteidol', 'deleteidols'])
    @is_mod()
    async def delete_idols(self, ctx, group, *args):
        """
        Deletes all idol(s) specified in a group
        Example: .delete_idols <group> <idol_1> <idol_2>
        """
        group = group.lower()
        g_id = find_group_id(group)
        if not g_id:
            await ctx.send(embed=error_embed(f'No group added named {group}!'))
            return

        if not args:
            await ctx.send(embed=error_embed('No idols provided!'))
        else:
            members = get_members_of_group(group)
            members = [x[0] for x in members]
            members = set(members)
            args = set(args)
            idol_list = members.intersection(args)
            failed = args - members
            success = []
            for idol in idol_list:
                idol = idol.lower()
                a = remove_member(g_id[0], idol)
                if a:
                    success.append(idol)
            if success and failed:
                s = ', '.join(success)
                f = ', '.join(failed)
                act = f"Deleted {s} from {group}."
                await moderation_auditing(self.disclient, ctx.author, act)
                await ctx.send(embed=success_embed(f'Deleted: {s}!\nFailed to delete {f}!'))
            elif success and not failed:
                s = ', '.join(success)
                act = f"Deleted: {s} from {group}!"
                await moderation_auditing(self.disclient, ctx.author, act)
                await ctx.send(embed=success_embed(act))
            else:
                f = ', '.join(failed)
                await ctx.send(embed=error_embed(f'Failed to delete {f}'))

    @commands.command(aliases=['addauditing'])
    @is_mod()
    async def add_auditing(self, ctx):
        """Adds auditing from this channel, as links are added to
        the bot, they will also be posted here so all new additions
        can be viewed."""
        if not check_user_is_mod(ctx):
            await ctx.send(embed=permission_denied_embed())
            return

        add_channel(ctx.channel.id)
        added = add_auditing_channel(ctx.channel.id)
        if added:
            des = 'Added this channel to the auditing list!'
            await ctx.send(embed=success_embed(des))
        else:
            des = 'Channel already in auditing list!'
            await ctx.send(embed=error_embed(des))

    @commands.command(aliases=['removeauditing'])
    @is_mod()
    async def remove_auditing(self, ctx):
        """Removes auditing from this channel!"""
        removed = remove_auditing_channel(ctx.channel.id)
        if removed:
            des = 'Removed this channel from the auditing list!'
            await ctx.send(embed=success_embed(des))
        else:
            des = 'Channel not in the auditing list!'
            await ctx.send(embed=error_embed(des))

    @commands.command(aliases=['delcommand', 'dc'])
    @is_mod()
    async def delete_command(self, ctx, command):
        """Removes a custom command created previously."""
        command = command.lower()
        removed = remove_command(command)
        if removed:
            act = f"Removed command: {command}"
            await moderation_auditing(self.disclient, ctx.author, act)
            await ctx.send(embed=success_embed(f'Removed {command}!'))
        else:
            await ctx.send(embed=error_embed(f'Command {command} does not exist!'))

    @add_group_alias.on_autocomplete("group")
    @add_idols.on_autocomplete("group")
    @add_idol_alias.on_autocomplete("group")
    @delete_idol_alias.on_autocomplete("group")
    async def group_picker(self, interaction: discord.Interaction, group_name: str):
        if not group_name:
            await interaction.response.send_autocomplete(pick_groups())
            return
        get_near_groups = [group for group in pick_groups(near=group_name) if
                           group.lower().startswith(group_name.lower())]
        await interaction.response.send_autocomplete(get_near_groups)

    @add_idol_alias.on_autocomplete("idol")
    @delete_idol_alias.on_autocomplete("idol")
    async def idol_picker(self, interaction: discord.Interaction, idol_name: str):
        group = interaction.data['options'][0]['value']
        if not idol_name:
            await interaction.response.send_autocomplete()
            return
        get_near_idols = [i for i in pick_group_members(group) if i.startswith(idol_name)]
        await interaction.response.send_autocomplete(get_near_idols)

    @delete_group_alias.on_autocomplete("alias")
    async def group_alias_picker(self, interaction: discord.Interaction, alias_name: str):
        group = interaction.data['options'][0]['value']
        if not alias_name:
            await interaction.response.send_autocomplete(get_group_aliases(group))
            return
        get_near_aliases = [a for a in get_group_aliases(group) if a.startswith(alias_name)]
        await interaction.response.send_autocomplete(get_near_aliases)


async def moderation_auditing(disclient, author, action):
    """Posts moderator actions to the mod auditing channel in the discord."""
    mod_audcha = disclient.get_channel(apis_dict["mod_audit_channel"])
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    s = f'`{dt}`: `{author}`:\n{action}'
    embed = discord.Embed(title=s,
                          color=discord.Color.blurple())
    await mod_audcha.send(embed=embed)


def setup(disclient):
    disclient.add_cog(Moderation(disclient))
    disclient.add_cog(Owner(disclient))
