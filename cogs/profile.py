import asyncio
import os

import aiosqlite
import discord
from discord import  app_commands
from discord.ext import commands

from master import MasterCog


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='profile_build')
    @commands.is_owner()
    @commands.guild_only()
    async def build_profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if os.path.isfile(f'config/{interaction.guild_id}/profile.db'):
            await interaction.edit_original_response(embed =discord.Embed(title="Do you want to initiate new database? A file already exists."))
            reply = await interaction.original_response()
            await reply.add_reaction('👍')
            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) == '👍'
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
            except asyncio.TimeoutError:
                await interaction.edit_original_response(embed=discord.Embed(title='You waited too long. 👎'))
                await reply.clear_reactions()

            if str(reaction) != '👍' or user != interaction.user:
                await interaction.edit_original_response(embed=discord.Embed(title='Something went wrong.'))
                return
            elif str(reaction) == '👍' and user == interaction.user:
                await reply.clear_reactions()
                os.remove(f'config/{interaction.guild_id}/profile.db')
            else:
                await interaction.edit_original_response(embed=discord.Embed(title='Something went wrong.'))
                return
        elif not os.path.isfile(f'config/{interaction.guild_id}/profile.db'):
            await interaction.edit_original_response(embed =discord.Embed(title="No Database Found. Creating New One"))
        sql = """CREATE TABLE IF NOT EXISTS profiles 
                            (id INTEGER PRIMARY KEY,
                            playstation TEXT, 
                            microsoft TEXT, 
                            bungie TEXT,
                            xiv TEXT, 
                            steam TEXT,
                            warframe TEXT,
                            battle_net TEXT);"""
        await MasterCog.execute(MasterCog(self), sql, interaction.guild_id,"profile", commit = True)

        for member in interaction.guild.members:
            if not member.bot:
                await self.add_profile(interaction.guild_id, member)
        await interaction.followup.send(embed=discord.Embed(title="Profile database built."))

    async def add_profile(self, guild_id: int, member: discord.Member):
        sql = """INSERT INTO profiles (id,playstation,microsoft,bungie, xiv, steam, warframe, battle_net) 
        VALUES (?,?,?,?,?,?,?,?)"""
        parameters = (member.id, "", "", "", "", "", "", "")
        await MasterCog.execute(MasterCog(self), sql, guild_id,"profile", parameters, commit=True)

    async def del_profile(self, guild_id: int, member: discord.Member):
        sql = f"""DELETE FROM profiles
                WHERE id = {member.id};"""
        await MasterCog.execute(MasterCog(self), sql,guild_id,"profile",commit=True)

    @app_commands.command(name='profile_set')
    @app_commands.choices(account = [
        app_commands.Choice(name="Playstation", value="playstation"),
        app_commands.Choice(name="Microsoft", value="microsoft"),
        app_commands.Choice(name="Bungie", value="bungie"),
        app_commands.Choice(name="Final Fantasy XIV", value="xiv"),
        app_commands.Choice(name="Steam", value="steam"),
        app_commands.Choice(name="Warframe", value="warframe"),
        app_commands.Choice(name="Battle.Net", value="battle_net")
    ])
    @commands.guild_only()
    async def set(self, interaction:discord.Interaction, account: str, username: str):
        """Add your usernames for your accounts"""
        if len(username) > 32:
            await interaction.response.send_message(
                embed=discord.Embed(title='**[Error]** : Usernames must be 32 characters or less'), ephemeral=True)
            return
        sql = f"""UPDATE profiles
        SET {account} = ?
        WHERE id = ?;"""

        parameters = (username, interaction.user.id)
        await MasterCog.execute(MasterCog(self), sql,interaction.guild_id,"profile",parameters,commit=True)

        if "xiv" in account:
            account = "Final Fantasy XIV"
        elif "battle_net" in account:
            account = "Battle.Net"
        else:
            account = account.capitalize()
        await interaction.response.send_message(embed=discord.Embed(title=f"{account} username changed to "
                                                                              f"{username}"), ephemeral=True)

    @app_commands.command(name='profile_delete')
    @app_commands.choices(account=[
        app_commands.Choice(name="Playstation", value="playstation"),
        app_commands.Choice(name="Microsoft", value="microsoft"),
        app_commands.Choice(name="Bungie", value="bungie"),
        app_commands.Choice(name="Final Fantasy XIV", value="xiv"),
        app_commands.Choice(name="Steam", value="steam"),
        app_commands.Choice(name="Warframe", value="warframe"),
        app_commands.Choice(name="Battle.Net", value="battle_net")
    ])
    @commands.guild_only()
    async def delete(self, interaction: discord.Interaction, account: str):
        """Delete a username"""
        sql = f"""UPDATE profiles
            SET {account} = ?
            WHERE id = ?;"""
        parameters = ("", interaction.user.id)
        await MasterCog.execute(MasterCog(self), sql, interaction.guild_id,"profile", parameters, commit=True)
        if "xiv" in account:
            account = "Final Fantasy XIV"
        elif "battle_net" in account:
            account = "Battle.Net"
        else:
            account = account.capitalize()

        await interaction.response.send_message(embed=discord.Embed(title=f"{account} has been removed."), ephemeral=True)

    @commands.has_permissions(manage_messages=True)
    @app_commands.command(name="profile_staff_set")
    @app_commands.choices(account = [
        app_commands.Choice(name="Playstation", value="playstation"),
        app_commands.Choice(name="Microsoft", value="microsoft"),
        app_commands.Choice(name="Bungie", value="bungie"),
        app_commands.Choice(name="Final Fantasy XIV", value="xiv"),
        app_commands.Choice(name="Steam", value="steam"),
        app_commands.Choice(name="Warframe", value="warframe"),
        app_commands.Choice(name="Battle.Net", value="battle_net")
    ])
    async def staff_set(self, interaction: discord.Interaction, member: discord.Member, account: str, username: str):
        """For staff to add a username for a user."""
        if len(username) > 32:
            await interaction.response.send_message(
                embed=discord.Embed(title='**[Error]** : Usernames must be 32 characters or less'), ephemeral=True)
            return
        sql = f"""UPDATE profiles
        SET {account} = ?
        WHERE id = ?;"""
        parameters = (username, member.id)
        await MasterCog.execute(MasterCog(self), sql,interaction.guild_id,parameters,"profile",commit=True)

        if "xiv" in account:
            account = "Final Fantasy XIV"
        elif "battle_net" in account:
            account = "Battle.Net"
        else:
            account = account.capitalize()

        await interaction.response.send_message(embed=discord.Embed(title=f"{account} username for "
                                                                              f"{member.display_name} changed to "
                                                                              f"{username}"), ephemeral=True)


    @commands.has_permissions(manage_messages=True)
    @app_commands.command(name="profile_staff_del")
    @app_commands.choices(account=[
        app_commands.Choice(name="Playstation", value="playstation"),
        app_commands.Choice(name="Microsoft", value="microsoft"),
        app_commands.Choice(name="Bungie", value="bungie"),
        app_commands.Choice(name="Final Fantasy XIV", value="xiv"),
        app_commands.Choice(name="Steam", value="steam"),
        app_commands.Choice(name="Warframe", value="warframe"),
        app_commands.Choice(name="Battle.Net", value="battle_net")
    ])
    @commands.guild_only()
    async def staff_del(self, interaction: discord.Interaction, member: discord.Member, account: str):
        """Staff use to delete a username"""
        sql = f"""UPDATE profiles
                    SET {account} = ?
                    WHERE id = ?;"""
        parameters = ("", member.id)
        await MasterCog.execute(MasterCog(self),sql, interaction.guild_id,"profile", parameters, commit=True)
        if "xiv" in account:
            account = "Final Fantasy XIV"
        elif "battle_net" in account:
            account = "Battle.Net"
        else:
            account = account.capitalize()

        await interaction.response.send_message(embed=discord.Embed(title=f"{account} for {member.display_name} "
                                                                    f"has been removed."), ephemeral=True)

    @app_commands.command(name='get_username')
    @app_commands.choices(account=[
        app_commands.Choice(name="Playstation", value="playstation"),
        app_commands.Choice(name="Microsoft", value="microsoft"),
        app_commands.Choice(name="Bungie", value="bungie"),
        app_commands.Choice(name="Final Fantasy XIV", value="xiv"),
        app_commands.Choice(name="Steam", value="steam"),
        app_commands.Choice(name="Warframe", value="warframe"),
        app_commands.Choice(name="Battle.Net", value="battle_net")
    ])
    @commands.guild_only()
    async def get(self, interaction: discord.Interaction, account: str, member: discord.Member = None):
        """Get a users usernames. Defaults to yourself"""
        if member is None:
            member = interaction.user
        sql = f"""SELECT {account} FROM profiles
                WHERE id = {member.id}"""
        data = await MasterCog.execute(MasterCog(self), sql,interaction.guild_id,"profile",fetchone=True)

        if "xiv" in account:
            account = "Final Fantasy XIV"
        elif "battle_net" in account:
            account = "Battle.Net"
        else:
            account = account.capitalize()

        if data[0] == "":
            await interaction.response.send_message(embed=discord.Embed(title=f"No Username found for {account}"))
        else:
            username = data[0]
        await interaction.response.send_message(embed=discord.Embed(title=f'{account} username: *{username}*',
                                           color=discord.Colour.gold()))


    @app_commands.command(name="profile_get")
    @commands.guild_only()
    async def profile(self, interaction:discord.Interaction, member: discord.Member = None):
        """Displays a profile."""
        await interaction.response.defer()
        if member is None:
            member = interaction.user

        sql = f"""SELECT * FROM profiles
                WHERE id = {member.id}"""

        data = await MasterCog.execute(MasterCog(self), sql,interaction.guild_id, "profile",fetchall=True)

        embed = discord.Embed(title=f"{member.display_name}'s Profile!")
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.set_footer(text=f'Results provided by: {self.bot.user.name}', icon_url=self.bot.user.avatar.url)
        counter = 0
        for i in range(1,8):
            if data[0][i] == "":
                counter += 1
                if counter == 7:
                    embed.add_field(name=f"**No profile data found.**", value="")
                continue
            if i == 1:
                account = "Playstation"
            elif i == 2:
                account = "Microsoft"
            elif i == 3:
                account = "Bungie"
            elif i == 4:
                account = "Final Fantasy XIV"
            elif i == 5:
                account = "Steam"
            elif i == 6:
                account = "Warframe"
            elif i == 7:
                account = "Battle.Net"
            embed.add_field(name=f"__**{account}:**__", value=f"{data[0][i]}")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Profile(bot))
