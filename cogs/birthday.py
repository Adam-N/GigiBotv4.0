import asyncio
import json
import os

import discord
from discord import app_commands
from discord.ext import commands, tasks

import datetime as dt

from master import MasterCog


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.remove_birthday.start()

    def cog_unload(self):
        self.remove_birthday.cancel()

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        sql = """DELETE FROM users WHERE id = ?;"""
        await MasterCog.execute(MasterCog(self), sql, payload.guild_id, "birthday", (payload.user.id,))

    @app_commands.command(name='create_birthday_db')
    @commands.is_owner()
    async def create_birthday_db(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # Checks if there's a valid db file.
        if os.path.isfile(f'config/{interaction.guild_id}/birthday.db'):
            # This is a check to see if you want to overwrite the db file.
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
            # This is the option to continue.
            elif str(reaction) == '👍' and user == interaction.user:
                await reply.clear_reactions()
                os.remove(f'config/{interaction.guild_id}/birthday.db')
            else:
                await interaction.edit_original_response(embed=discord.Embed(title='Something went wrong.'))
                return
        elif not os.path.isfile(f'config/{interaction.guild_id}/birthday.db'):
            await interaction.edit_original_response(embed =discord.Embed(title="No Database Found. Creating New One"))

        sql = """CREATE TABLE IF NOT EXISTS users 
                                    (id INTEGER PRIMARY KEY,
                                    date TEXT,
                                    last_wish TEXT);"""
        await MasterCog.execute(MasterCog(self), sql, interaction.guild_id, "birthday",commit=True)
        await interaction.edit_original_response(embed=discord.Embed(title='Completed Database Build.', type="rich"))

    @app_commands.command(name="birthday")
    @commands.guild_only()
    @commands.has_permissions(manage_permissions=True)
    async def birthday(self, interaction: discord.Interaction, user: discord.Member):
        #Defers so it can take longer than 3 s to respond.
        await interaction.response.defer(ephemeral=True)
        # Gets config file.
        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
        # Gets birthday role.
        birthday_role = interaction.guild.get_role(int(config['role_config']["birthday"]))

        # Formats a date to add to the db.
        today = dt.date.today()
        date = f"{today.month}/{today.day}"

        sql = f"""SELECT * FROM users where id = {user.id}"""
        data = await MasterCog.execute(MasterCog(self), sql, interaction.guild_id, "birthday", fetchone=True)
        if data:
            # This checks to see if they're user_id is in the db on a different date and returns if it is.
            if data[1] != date:
                await interaction.followup.send(
                    embed=discord.Embed(title=f"It appears they already have different birthday listed this year. "
                                              f"Date: {date[1]}"), ephemeral=True)
                return

            # This checks to see if they've been wished a birthday in the last 360 days.
            elif data[1] != date and dt.datetime.now() <= dt.datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S") + \
                    dt.timedelta(days=300):
                day_delay_embed = discord.Embed(
                    title="\U0001f550 You have to wait until next year! \U0001f550 ")
                await interaction.followup.send(embed=day_delay_embed, ephemeral=True)
                return

        # Upserts user info into user table for the timestamp to check against.
        sql = """INSERT INTO users(id, date, last_wish) VALUES(?,?,?)
                ON CONFLICT(id)
                DO UPDATE
                SET last_wish = excluded.last_wish;"""
        await MasterCog.execute(MasterCog(self), sql, interaction.guild_id, "birthday",
                                (user.id, date, str(dt.datetime.strftime(dt.datetime.now(),
                                                                     "%Y-%m-%d %H:%M:%S"))), commit=True)

        # Adds role and sends message.
        await user.add_roles(birthday_role)
        lounge_channel = interaction.guild.get_channel(int(config['channel_config']['lounge']))

        birthday_embed = discord.Embed(title=f"It's {user.display_name}'s birthday! ",
                                       description= "We hope all your birthday wishes come "
                                                    "true - except the illegal ones! Here's "
                                                    "to you and your time here with us. "
                                                    "Another year older, another year in "
                                                    "the posse! Happy birthday! :birthday:")
        birthday_embed.set_image(url="https://media.discordapp.net/attachments/532380077896237061/1332900829837000814"
                                     "/gigi_birthdaysmall.png?ex=679798e1&is=67964761&hm=6bfb4cbabbc6bd58b2cb9899baab"
                                     "56e836aece62c7bfaa7cf3738ebd2f0b26c8&=&format=webp&quality=lossless&width="
                                     "625&height=625")

        await lounge_channel.send(embed=birthday_embed)
        await interaction.followup.send(f"Birthday given to {user.display_name}", ephemeral=True)

    @app_commands.command(name="birthday_add")
    @commands.is_owner()
    async def add_birthday(self, interaction: discord.Interaction, user: discord.User, month:int, day:int):
        sql = """INSERT INTO users(id, date, last_wish) VALUES(?,?,?)
                        ON CONFLICT(id)
                        DO NOTHING;"""
        last_wish  = dt.datetime.strftime(dt.date(year=2023, day=day, month=month),"%Y-%m-%d %H:%M:%S")

        await MasterCog.execute(MasterCog(self), sql, interaction.guild_id,"birthday", (user.id,
                                                                                    f"{month}/{day}", last_wish),
                                                                                    commit=True)
        await interaction.response.send_message("User added birthday." , ephemeral=True)

    @app_commands.command(name="birthday_del")
    @commands.is_owner()
    async def rem_birthday(self, interaction: discord.Interaction, user: discord.User):
        sql = """DELETE FROM users WHERE id = ?;"""
        await MasterCog.execute(MasterCog(self), sql, interaction.guild_id, "birthday", (user.id,),
                                commit=True)
        await interaction.response.send_message("Deleted from the table.", ephemeral=True)

    @tasks.loop(hours = 8)
    async def remove_birthday(self):
        guild_id = 334925467431862272
        if os.path.isfile(f'config/{guild_id}/config.json'):
            with open(f'config/{guild_id}/config.json', 'r') as f:
                config = json.load(f)

            guild = self.bot.get_guild(guild_id)
            role = guild.get_role(config['role_config']['birthday'])
            guild = guild
            for member in role.members:
                sql = f"""SELECT * FROM users WHERE id = (?)"""
                user_check = await MasterCog.execute(MasterCog(self),sql, guild_id,"birthday", (member.id,), fetchone=True)
                if user_check:
                    if dt.datetime.now() <= dt.datetime.strptime(user_check[2], "%Y-%m-%d %H:%M:%S") + \
                            dt.timedelta(hours=24):
                        await member.remove_roles(role)
                        config_channel= guild.get_channel(config["channel_config"]["config_channel"])
                        await config_channel.send(f"{member.display_name} had birthday role removed.")


    async def daily_birthday(self,guild_id):
        if os.path.isfile(f'config/{guild_id}/config.json'):
            with open(f'config/{guild_id}/config.json', 'r') as f:
                config = json.load(f)
        today = dt.date.today()
        date = f"{today.month}/{today.day}"
        guild = self.bot.get_guild(guild_id)
        config_channel = guild.get_channel(config["channel_config"]["config_channel"])
        sql = f"""SELECT * FROM users where date = (?)"""

        data = await MasterCog.execute(MasterCog(self), sql, guild_id,"birthday",(date,)
                                       , fetchall=True)
        embed = discord.Embed(title="These users have birthdays today!")
        if not data:
            return
        user_str = ""
        for user in data:
            print(user)
            member = await guild.fetch_member(user[0])
            embed.add_field(name= f"Username: {member.display_name}", value=f"User ID: {str(member.id)}")

        await config_channel.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Birthday(bot))
