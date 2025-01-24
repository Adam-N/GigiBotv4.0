import aiosqlite
import discord
from discord import  app_commands
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='profile_build')
    @commands.is_owner()
    @commands.guild_only()
    async def build_profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        sql = """CREATE TABLE IF NOT EXISTS profiles 
                            (id INTEGER PRIMARY KEY,
                            playstation TEXT, 
                            microsoft TEXT, 
                            bungie TEXT,
                            xiv TEXT, 
                            steam TEXT,
                            warframe TEXT,
                            battle_net TEXT);"""
        await self.execute(sql, interaction.guild_id, commit = True)

        for member in interaction.guild.members:
            if not member.bot:
                await self.add_profile(interaction.guild_id, member)
        await interaction.followup.send(embed=discord.Embed(title="Profile database built."))

    async def add_profile(self, guild_id: int, member: discord.Member):
        sql = """INSERT INTO profiles (id,playstation,microsoft,bungie, xiv, steam, warframe, battle_net) 
        VALUES (?,?,?,?,?,?,?,?)"""
        parameters = (member.id, "", "", "", "", "", "", "")
        await self.execute(sql, guild_id, parameters, commit=True)

    async def del_profile(self, guild_id: int, member: discord.Member):
        sql = f"""DELETE FROM profiles
                WHERE id = {member.id};"""
        await self.execute(sql,guild_id,commit=True)

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
        await self.execute(sql,interaction.guild_id,parameters,commit=True)

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
        await self.execute(sql, interaction.guild_id, parameters, commit=True)
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
        await self.execute(sql,interaction.guild_id,parameters,commit=True)

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
        await self.execute(sql, interaction.guild_id, parameters, commit=True)
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
        data = await self.execute(sql,interaction.guild_id,fetchone=True)

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

        data = await self.execute(sql,interaction.guild_id,fetchall=True)

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

    async def execute(self, sql: str,guild_id:int, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        async with aiosqlite.connect(f'config/{guild_id}/profile.db') as db:
            if not parameters:
                parameters = ()
            data = None
            cursor = await db.cursor()
            await cursor.execute(sql, parameters)
            if commit:
                await db.commit()
            if fetchone:
                data = await cursor.fetchone()
            if fetchall:
                data = await cursor.fetchall()
            return data

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Profile(bot))
