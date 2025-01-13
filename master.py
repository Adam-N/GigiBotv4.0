import os
import json
from typing import List

import time
import emoji
import discord
from discord import app_commands
from discord.ext import commands
from time import time
import datetime as dt


from lib.util import Util

class MasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_db = None
        self.start_time = time()
        self.sys_aliases = {'ps': {'ps', 'psn', 'ps4', 'ps5', 'playstation'},
                            'steam': {'steam', 'steam64', 'valve'},
                            'dtg': {'destiny', 'bungie', 'Bungie', 'destiny2'},
                            'xiv': {'ffxiv', 'xiv', 'ff'}}

        super().__init__()



    @app_commands.command(name="change_config", description="This is used to change the config of the active server.")
    @commands.is_owner()
    async def config(self, interaction: discord.Interaction, cfg: str, setting: str, value: str, delete: bool = None):
        """This is used to change the config of the active server."""
        # You only have 3 seconds to respond. So to make sure we don't time out use defer
        await interaction.response.defer()
        channel, role, emojiobj, emojistr = None, None, None, None
        ctx = await self.bot.get_context(interaction)  # Context is needed in this style for stuff later.

        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
            try:
                # Sees if the value given is a channel id.
                value = await commands.TextChannelConverter().convert(ctx, value)
                channel = value
                value = value.id
            except (TypeError, commands.errors.ChannelNotFound):
                pass
            try:
                # Checks to see if role id is given.
                value = await commands.RoleConverter().convert(ctx, value)
                role = value
                value = value.id
            except (TypeError, commands.errors.RoleNotFound):
                pass
            try:
                # Checks to see if a custom id is given.
                emojiobj = await commands.EmojiConverter().convert(ctx, value)
                value = emojiobj.id
            except (TypeError, commands.errors.EmojiNotFound):
                try:
                    # This throws an error if it is an int. That doesn't get caught by ValueError.
                    if not channel and not role and not emojiobj and "threshold" not in setting:
                        # This checks if it only contains emojis.
                        emoji.purely_emoji(value)
                        emojistr = value
                except ValueError:
                    pass
            try:
                if value.isdigit():
                    value = int(value)
            except AttributeError:
                pass
            try:
                # Checks if the setting is a list, then uses append to add to it.
                if isinstance(config[cfg][setting], list):
                    if delete is not None:
                        config[cfg][setting].remove(value)
                    else:
                        config[cfg][setting].append(value)
                else:
                    config[cfg][setting] = value
            except KeyError:
                # Error Response
                await interaction.followup.send(
                    embed=discord.Embed(title=f'**[Error]** : \"{setting}\" is not defined', type="rich"))
                return
            # Checks names of settings to what has been located and sends a message.
            if ("channel" in cfg or "channel" in setting) and not channel:
                await interaction.followup.send(
                    embed=discord.Embed(title=f"You're trying to update a channel setting and provided no channel ID.", type="rich"))
                return
            if ("role" in cfg or "role" in setting) and not role:
                await interaction.followup.send(
                    embed=discord.Embed(title=f"You're trying to update a role setting and provided no role info.", type="rich"))
                return
            if ("react" in cfg or "react" in setting) and (not emojiobj and not emojistr):
                await interaction.followup.send(
                    embed=discord.Embed(
                        title=f"You're trying to update a reaction setting and provided no emoji information.", type="rich"))
                return
            with open(f'config/{interaction.guild_id}/config.json', 'w') as f:
                json.dump(config, f, indent=2)

            # Builds the embed for sending. For Followups embeds MUST be rich.
            embed = discord.Embed(title='Updated configuration',
                                          description=f'**Config** : {cfg}\n**Setting** : {setting}', type="rich")
            if channel and not isinstance(config[cfg][setting], list):
                embed.add_field(name=f"Channel Change", value=channel.mention)
            elif channel and isinstance(config[cfg][setting], list):
                embed.add_field(name=f"Channel Add", value=channel.mention)
            elif role and not isinstance(config[cfg][setting], list):
                embed.add_field(name=f"Role Change", value=role.mention)
            elif role and isinstance(config[cfg][setting], list):
                embed.add_field(name=f"Role Add", value=role.mention)
            elif emojiobj:
                embed.add_field(name=f"Custom Emoji Add", value=f"<{emojiobj.name}:{emojiobj.id}> \n {emojiobj}")
            elif emojistr and "threshold" not in setting:
                embed.add_field(name=f"Unicode Emoji Add", value=f"{emojistr}")
            else:
                embed.add_field(name="Value", value=value)
            #Sends follow-up message. Have you use followup due to having a response earlier (defer)
            await interaction.followup.send(embed=embed)

    #These are to populate the autocompletes for the config command.
    # Removing everything that's unused in the function breaks this. i.e current.
    @config.autocomplete('cfg')
    async def config_pick_1(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
        # This is for the top level selections in the Config
        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
            choices_list = []
            for key in config.keys():
                name = ""
                list_for_name = []
                # We don't change the prefix through any programs that use this function so we can exclude it.
                if key == "prefix":
                    continue
                list_for_name = key.split("_")
                for word in list_for_name:
                    name += word.capitalize() + " "
                choices_list.append(app_commands.Choice(name=name, value=key))
            return choices_list

    # Removing everything that's unused in the function breaks this. i.e current.
    @config.autocomplete('setting')
    async def second_auto(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
        first_choice = interaction.namespace["cfg"]
        # return list of Choice based on `first_choice`
        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
            choices_list = []
            for value in config[first_choice]:
                choices_list.append(app_commands.Choice(name=value, value=value))
            return choices_list

    @app_commands.command(name="ping",description="Pong. Shows the bot ping in milliseconds.")
    @commands.is_owner()
    async def ping(self, interaction: discord.Interaction):
        """Shows the bot ping in milliseconds."""
        await interaction.response.send_message(content=f':ping_pong: **Pong!**⠀{round(self.bot.latency, 3)}ms')

    @app_commands.command(name='uptime', description="Checking uptime.")
    async def uptime(self, interaction: discord.Interaction):
        """Shows the uptime for the bot."""
        if await Util.check_channel(await self.bot.get_context(interaction)):
            current_time = time()
            difference = int(round(current_time - self.start_time))
            time_converted = dt.timedelta(seconds=difference)
            Util.deltaconv(int(time_converted.total_seconds()))
            new_embed = discord.Embed()
            new_embed.add_field(name="Uptime", value=f'{Util.deltaconv(int(time_converted.total_seconds()))}',
                                inline=True)
            new_embed.set_thumbnail(url='https://media.discordapp.net/attachments/742389103890268281/746419792000319580'
                                        '/shiinabat_by_erickiwi_de3oa60-pre.png?width=653&height=672')
            await interaction.response.send_message(embed=new_embed)

    @app_commands.command(name="change_prefix", description="For changing the prefix for the current server.")
    @commands.is_owner()
    async def change_prefix(self, interaction: discord.Interaction, prefix: str):
        """Changes the prefix for the current server. Only needed for hybrid commands."""
        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
            if interaction.channel.id == config['channel_config']['config_channel']:
                if len(prefix) > 3:
                    await interaction.response.send_message(embed=discord.Embed(title='Bot prefix must be 3 or less characters'))
                    return
                config['prefix'] = prefix
                with open(f'config/{interaction.guild_id}/config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                await interaction.response.send_message(embed=discord.Embed(title=f'Prefix changed to {prefix}'))

    @app_commands.command(name='reset_config')
    @commands.is_owner()
    async def reset_config(self, interaction:discord.Interaction):
        """Resets the servers config file. Only use when something is broken."""
        await Util.reset_config(await self.bot.get_context(interaction))


   
    @app_commands.command(name="setstatus")
    @commands.is_owner()
    @app_commands.choices(
        activity=[
            app_commands.Choice(name="Playing", value="playing"),
            app_commands.Choice(name="Listening", value="listening"),
            app_commands.Choice(name="Watching", value="watching")
        ])
    async def status(self, ctx, activity: str, status: str):
        """"For changing the activity that shows up for Gigi"""
        await ctx.defer()
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if ctx.channel.id == config['channel_config']['config_channel']:
                activity = activity.lower()
                if activity not in ['playing', 'listening', 'watching']:
                    await ctx.reply('Only playing, streaming, listening or watching allowed as activities.',
                                           delete_after=5)
                    return
                elif activity == 'playing':
                    await self.bot.change_presence(activity=discord.Game(name=status))
                elif activity == 'listening':
                    await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
                elif activity == 'watching':
                    await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
                await ctx.send(f'status changed to {activity} {status}')

    @commands.hybrid_command(name="load", description="To load cogs.", hidden=True)
    @commands.is_owner()
    async def load(self, ctx, cog: str):

        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if ctx.channel.id == config['channel_config']['config_channel']:
                try:
                    await self.bot.load_extension(cog)
                except Exception as e:
                    await discord.Message.add_reaction(ctx.message, '\U0000274E')
                    await ctx.send(f'Failed to load module: {type(e).__name__} - {e}', delete_after=10)
                else:
                    await discord.Message.add_reaction(ctx.message, '\U00002705')
            else: await ctx.send(f"This is not the appropriate channel. You must use "
                                 f"{self.bot.get_channel(int(config['channel_config']['config_channel'])).mention}")
        else:
            await discord.Message.add_reaction(ctx.message, '\U0000274E')
            await ctx.send(f'Failed to load module: no config file', delete_after=10)



    @commands.hybrid_command(name='unload', hidden=True, description="To unload cogs")
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Administrator command. For unloading cogs."""
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if ctx.channel.id == config['channel_config']['config_channel']:
                try:
                    await self.bot.unload_extension(cog)
                except Exception as e:
                    await discord.Message.add_reaction(ctx.message, '\U0000274E')
                    await ctx.send(f'Failed to unload module: {type(e).__name__} - {e}'), #delete_after=10)
                else:
                    await discord.Message.add_reaction(ctx.message, '\U00002705')
            else: await ctx.send(f"This is not the appropriate channel. You must use "
                                 f"{self.bot.get_channel(int(config['channel_config']['config_channel'])).mention}")
        else:
            await discord.Message.add_reaction(ctx.message, '\U0000274E')
            await ctx.send(f'Failed to load module: no config file', delete_after=10)

    @commands.hybrid_command(name='reload', hidden=True, description="For reloading Cogs")
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        """Administrator command. For reloading cogs"""
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if ctx.channel.id == config['channel_config']['config_channel']:
                try:
                    await self.bot.unload_extension(cog)
                    await self.bot.load_extension(cog)
                except Exception as e:
                    await discord.Message.add_reaction(ctx.message, '\U0000274E')
                    await ctx.send(f'Failed to reload module: {type(e).__name__} - {e}', delete_after=10)

                else:
                    await discord.Message.add_reaction(ctx.message, '\U00002705')
            else: await ctx.send(f"This is not the appropriate channel. You must use "
                                 f"{self.bot.get_channel(int(config['channel_config']['config_channel'])).mention}")
        else:
            await discord.Message.add_reaction(ctx.message, '\U0000274E')
            await ctx.send(f'Failed to load module: no config file', delete_after=10)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MasterCog(bot))
