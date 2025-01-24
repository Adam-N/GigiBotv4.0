import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions

from cogs.drive import Drive
from cogs.profile import Profile

from discord.errors import Forbidden


class Triumphant(commands.Cog, name='Triumphant'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='init_triumphant')
    @commands.is_owner()
    async def init_triumphant(self, interaction: discord.Interaction):
        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
            triumphant_config = {
                'triumph_channel': interaction.channel.id,
                'triumph_react': None
            }
            config['triumphant_config'] = triumphant_config
            with open(f'config/{interaction.guild_id}/config.json', 'w') as f:
                json.dump(config, f, indent=2)
            await interaction.response.send_message(embed=discord.Embed(title=f'Triumphant config initialized'))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if os.path.isfile(f'config/{str(payload.guild_id)}/config.json'):
            with open(f'config/{str(payload.guild_id)}/config.json', 'r') as f:
                config = json.load(f)

        if str(payload.emoji) not in config['triumphant_config']['triumph_react']:
            return
        guild = self.bot.get_guild(payload.guild_id)
        channel = await self.bot.fetch_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        not_bot_user = None
        id_list = []
        name_list = []
        name_list_for_upload = ""
        posting_channel = await self.bot.fetch_channel(int(config['triumphant_config']["triumph_channel"]))
        name_for_upload = ""
        for reaction in msg.reactions:
            async for user in reaction.users():
                if user.id == self.bot.user.id and str(payload.emoji) in config['triumphant_config']['triumph_react']:
                    return
        try:
            await msg.add_reaction(config['triumphant_config']['triumph_react'])
        except Forbidden:
            return
        results = []
        count = 0
        if msg.embeds:
            copy_embed = msg.embeds[0].to_dict()
            try:
                split_description = copy_embed['description'].split("**")
                description = split_description[1]
            except KeyError:
                description = ""
            for member in guild.members:
                if member.bot:
                    continue
                if member.name.lower() == description.lower() or member.display_name.lower() == description.lower():
                    not_bot_user = member.id
                    name_for_upload = member.display_name
                    break

            if not not_bot_user:
                sql = f"""SELECT * FROM profiles WHERE playstation = ? OR microsoft = ? 
                OR bungie = ? OR xiv = ? OR steam = ? OR warframe = ? OR battle_net = ?;"""

                user = await Profile.execute(self.bot,sql,guild.id,
                                             (description,description,description,
                                              description,description,description,description),fetchone=True)

                if user:
                    user = guild.get_member(int(user[0]))
                    results.append(user.display_name)
                    not_bot_user = user.id
                    name_for_upload = user.display_name
                elif not user:
                    sql = f"""SELECT * FROM profiles WHERE playstation = ? OR microsoft = ? 
                    OR bungie = ? OR xiv = ? OR steam = ? OR warframe = ? OR battle_net = ?;"""
                    try:
                        user = await Profile.execute(self.bot, sql, guild.id,(copy_embed["fields"][0]["value"],
                                                                          copy_embed["fields"][0]["value"],
                                                                          copy_embed["fields"][0]["value"],
                                                                          copy_embed["fields"][0]["value"],
                                                                          copy_embed["fields"][0]["value"],
                                                                          copy_embed["fields"][0]["value"],
                                                                          copy_embed["fields"][0]["value"]),
                                                                            fetchone=True)

                        if user:
                            user = guild.get_member(int(user[0]))
                            results.append(user.display_name)
                            not_bot_user = user.id
                            name_for_upload = user.display_name
                    except KeyError:
                        pass
            if msg.content:
                try:
                    content = msg.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["description"]}')
                except KeyError:
                    try:
                        content = msg.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["title"]}')
                    except KeyError:
                        pass
                    pass
            else:
                try:
                    content = copy_embed["description"]
                except KeyError:
                    content = copy_embed["title"]
            if "fields" in copy_embed:
                for embeds in msg.embeds:
                    try:
                        for field in embeds.fields:
                            content = content.__add__(f'\n\n**{field.name}**')
                            content = content.__add__(f'\n{field.value}')
                    except:
                        continue
        else:
            content = msg.content
            name_for_upload = payload.member.display_name
        if msg.mentions:
            for member in msg.mentions:
                id_list.append(str(member.id))
                name_list.append(str(member.display_name))
                name_list_for_upload = "People Mentioned: " + "\n".join(name_list)
        embed = discord.Embed(title=f"{msg.author} said...",
                              description=f'{content}\n\n[Jump to Message](https://discordapp.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id})',
                              colour=0x784fd7,
                              timestamp=msg.created_at)
        if not name_for_upload:
            name_for_upload = "No Discord Username found."
        content = (f"Discord Name of Nominee: {str(name_for_upload)} \n{name_list_for_upload} \n \nIn Channel: "
                   f"{channel.name} \n \nMessage:") + content
        await Drive.text_file(Drive(self.bot), text=content)

        if id_list:
            name_string = "\n".join(name_list)
            id_string = "\n".join(id_list)

            embed.add_field(name="People mentioned in the message:", value=name_string)
            embed.add_field(name="IDs:", value=id_string)
        if not msg.author.bot:
            embed.set_footer(text=f"ID:{msg.author.id}")
            try:

                embed.set_thumbnail(url=msg.author.avatar.url)
            except TypeError:
                pass
            embed.add_field(name="Nominated User:", value=f"{msg.author.name}")
        if msg.author.bot:
            if not_bot_user:
                embed.set_footer(text=f"ID:{not_bot_user}")
                avatar_member = await guild.fetch_member(not_bot_user)
                embed.set_thumbnail(url=avatar_member.avatar.url)
                embed.add_field(name="Nominated User:", value=f"{avatar_member.name}")
        if msg.embeds:
            if "image" in copy_embed:
                embed.set_image(url=copy_embed["image"]["url"])
            elif "video" in copy_embed:
                embed.set_image(url=copy_embed["thumbnail"]["url"])
        elif msg.attachments:
            embed.set_image(url=msg.attachments[0].url)
            await Drive.upload(Drive(self.bot), msg.attachments[0])

        embed.add_field(name='Nominated by:', value=f'{payload.member.name}')
        await posting_channel.send(embed=embed)
        if os.path.isfile(f'config/{payload.guild_id}/triumphant.json'):
            with open(f'config/{payload.guild_id}/triumphant.json', 'r') as f:
                users = json.load(f)
        else:
            users = {}
        if not msg.author.bot:
            users[str(msg.author.id)] = 1
        if msg.author.bot and not_bot_user:
            users[str(not_bot_user)] = 1
        if msg.mentions:
            for member in id_list:
                users[str(member)] = 1
        with open(f'config/{payload.guild_id}/triumphant.json', 'w') as f:
            json.dump(users, f)

    @app_commands.command(name="triumph_delete")
    @has_permissions(manage_messages=True)
    async def triumph_delete(self, interaction: discord.Interaction, member: discord.Member):
        with open(f'config/{interaction.guild_id}/triumphant.json', 'r') as f:
            users = json.load(f)
        try:
            if users[str(member.id)] == 1:
                del users[str(member.id)]
        except:
            del_embed = discord.Embed(title='User was not in the list')
            del_embed.add_field(name="User:", value=f"{member.name}")
            del_embed.add_field(name="User Id:", value=f"{member.id}")
            await interaction.response.send_message(embed=del_embed)
            return

        with open(f'config/{interaction.guild_id}/triumphant.json', 'w+') as f:
            json.dump(users, f)
        await interaction.response.send_message(embed = f"Succesfully deleted {member.name} from triumphant list. ID: {member.id}")

    @app_commands.command(name="triumph_add")
    @has_permissions(manage_messages=True)
    async def triumph_add(self, interaction: discord.Interaction, member: discord.Member):
        with open(f'config/{interaction.guild_id}/triumphant.json', 'r') as f:
            users = json.load(f)
        try:
            if users[str(member.id)]:
                add_embed = discord.Embed(title='User was already triumphant')
                add_embed.add_field(name="User:", value=f"{member.name}")
                add_embed.add_field(name="User Id:", value=f"{member.id}")
                await interaction.response.send_message(embed=add_embed)
                return
        except:
            users[str(member.id)] = 1

        with open(f'config/{interaction.guild_id}/triumphant.json', 'w') as f:
            json.dump(users, f)

        add_embed = discord.Embed(title='User is now triumphant')
        add_embed.add_field(name="User:", value=f"{member.name}")
        add_embed.add_field(name="User Id:", value=f"{member.id}")
        await interaction.response.send_message(embed=add_embed)

    @app_commands.command(name="triumph_list")
    @has_permissions(manage_messages=True)
    async def triumph_list(self, interaction:discord.Interaction, copy: str = None):
        id_list = ''
        user_list = ''

        if copy is None:
            with open(f'config/{interaction.guild_id}/triumphant.json', 'r') as f:
                users = json.load(f)
                copy = ""
        if copy:
            with open(f'config/{interaction.guild_id}/triumphant_copy.json', 'r') as f:
                users = json.load(f)

        for key in users:
            try:
                member = await interaction.guild.fetch_member(int(key))
                user_list = user_list + str(member.name) + " \n"
                id_list = id_list + key + " \n"
            except:
                continue
        list_embed = discord.Embed(title=f'Members on the triumphant list {copy}')
        list_embed.add_field(name='List:', value=f"{user_list}")
        list_embed.add_field(name="IDs:", value=f"{id_list}")
        await interaction.response.send_message(embed=list_embed)


    @app_commands.command(name="triumph_give")
    @has_permissions(manage_messages=True)
    async def give_triumphant(self, interaction: discord.Interaction):
        await interaction.response.defer()
        with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
            config = json.load(f)
        triumphant_role = interaction.guild.get_role(int(config['role_config']["triumphant"]))
        if triumphant_role:
            current_triumphant = list(triumphant_role.members)
        member_list = ""
        triumph_embed = discord.Embed(title="Triumphant Role Success",
                                      description="These users have received their role.")

        with open(f'config/{interaction.guild_id}/triumphant_copy.json', 'r') as f:
            users = json.load(f)
        if triumphant_role:
            for member in current_triumphant:
                await member.remove_roles(triumphant_role)
        for key in users:
            try:
                user = interaction.guild.get_member(int(key))
                member_list = member_list + user.display_name + '\n'
                await user.add_roles(triumphant_role)
            except AttributeError:
                continue
        os.remove(f'config/{interaction.guild_id}/triumphant_copy.json')
        triumph_embed.add_field(name="Users:", value=f"{member_list}")
        await interaction.followup.send(embed=triumph_embed)

    @app_commands.command(name="triumph_reset")
    @commands.is_owner()
    async def manual_reset(self, interaction:discord.Interaction):

        if os.path.isfile(f'config/{interaction.guild_id}/triumphant_copy.json'):
            await interaction.response.send_message("There was already a reset this week", ephemeral=True)
            return
        elif not os.path.isfile(f'config/{interaction.guild_id}/triumphant_copy.json') and os.path.isfile(
                f'config/{interaction.guild_id}/triumphant.json'):
            with open(f'config/{interaction.guild_id}/triumphant.json', 'r') as f:
                users = json.load(f)
            with open(f'config/{interaction.guild_id}/triumphant_copy.json', 'w') as f:
                json.dump(users, f)

            os.remove(f'config/{interaction.guild_id}/triumphant.json')

            triumphant = {}

            with open(f'config/{str(interaction.guild_id)}/triumphant.json', 'w') as f:
                json.dump(triumphant, f)

            reset_embed = discord.Embed(title="\U0001f5d3| New Week Starts Here. Get that bread!")
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
            chan = self.bot.get_channel(int(config['triumphant_config']["triumph_channel"]))

            await chan.send(embed=reset_embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Triumphant(bot))
