import asyncio
import os
import json
import random

import aiosqlite

import discord
from discord import app_commands
from discord.ext import commands


class Starboard(commands.Cog, name='Starboard'):
    def __init__(self, bot):
        self.bot = bot
        self.crab_url = 'https://cdn.discordapp.com/attachments/532380077896237061/1328120032210849918/crab-removebg-preview.png?ex=67858baa&is=67843a2a&hm=21185b380a5a8e7c0b0ba57bac1e60a7847f55e6eb59c10ed44bbfefd97c8a54&'
        self.lock = asyncio.Lock()

    @app_commands.command(name='init_starboard')
    @commands.is_owner()
    async def init_starboard(self, ctx):
        """Opens and resets or makes a new starboard config. """
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            starboard_config = {
                'starboard_channel': ctx.channel.id,
                'star_react': None,
                'starred_react': None,
                'threshold': 3
            }
            config['starboard_config'] = starboard_config
            with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
                json.dump(config, f, indent=2)
            await ctx.send(embed=discord.Embed(title=f'Starboard config initialized'))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Required Variables
        content = False
        self_starred = False
        already_posted = False
        list = None
        try:
            # Looks for and loads config
            if os.path.isfile(f'config/{payload.guild_id}/config.json'):
                with open(f'config/{payload.guild_id}/config.json', 'r') as f:
                    config = json.load(f)
            channel = self.bot.get_channel(payload.channel_id) # Channel where message was sent.
            # Get starboard channel.
            starboard_channel = self.bot.get_channel(config['starboard_config']['starboard_channel'])
            # Get the starred message.
            message = await channel.fetch_message(payload.message_id)
            # Gets emoji to use in message.
            emoji = self.bot.get_emoji(config["starboard_config"]["starred_react"])
            if emoji is None:
                emoji = config["starboard_config"]["starred_react"]

            # Locks for checking reactions.
            async with self.lock:
                for react in message.reactions:
                    if react.emoji == config['starboard_config']['star_react']:
                        # This is new in 2.0
                        list = [user async for user in react.users()]
                        # Checks if the author is someone who starred the message
                        # Gives them a self star if it's true.
                        if message.author in list:
                            self_starred = True
                        reaction = react
                        break
            if channel.id != starboard_channel.id:
                url = ""
                test_var = False
                # Checks to see if it is already posted in the Starboard by checking to see if the confirmation reaction
                # is there.
                already_posted = discord.utils.get(message.reactions, emoji=config['starboard_config']['starred_react'])

                if payload.emoji.name == config['starboard_config']['star_react']:
                    if reaction.count >= config['starboard_config']['threshold'] and not already_posted:
                        copy_embed = ""
                        if message.embeds:
                            copy_embed = message.embeds[0].to_dict()
                            try:
                                if copy_embed['footer']['text']:
                                    test_var = True
                            except KeyError:
                                pass
                            if message.content and not copy_embed['url']:
                                content = message.content.__add__(f'\n\n**Link Preview:**\n{copy_embed["description"]}')
                            elif message.content and copy_embed['url'] and not test_var:
                                try:
                                    content = " "
                                    url = copy_embed['url']
                                except:
                                    pass
                            else:
                                content = copy_embed["description"]
                                if not content:
                                    content = copy_embed['title']
                            if "fields" in copy_embed:
                                for embeds in message.embeds:
                                    for field in embeds.fields:
                                        content = str(content) + str(f'\n\n**{field.name}**')
                                        content = str(content) + str(f'\n{field.value}')
                        else:
                            content = message.content
                        if channel.type is discord.ChannelType.text:
                            embed = discord.Embed(title=f"{message.author} said...",
                                                  description=f'{content}\n\n[Jump to Message]({message.jump_url})',
                                                  colour=0x784fd7,
                                                  timestamp=message.created_at)
                        elif channel.type is discord.ChannelType.public_thread or channel.type is discord.ChannelType.public_thread:
                            embed = discord.Embed(title=f"{message.author} said...",
                                                  description=f'{content}',
                                                  colour=0x784fd7,
                                                  timestamp=message.created_at)
                        else:
                            embed = discord.Embed(title=f"{message.author} said...",
                                                  description=f'{content}',
                                                  colour=0x784fd7,
                                                  timestamp=message.created_at)
                        if message.author.avatar:
                            embed.set_thumbnail(url=message.author.avatar.url)

                        if message.attachments:
                            embed.set_image(url=message.attachments[0].url)
                        if not self_starred:
                            embed.set_footer(icon_url=self.crab_url, text='Original Posted')
                        elif self_starred:
                            embed.set_footer(icon_url=self.crab_url, text='Self-Crabbed')
                            await self.increment_table(payload.guild_id, "leaderboard",payload.member.id,
                                                       "self_starred")
                        if message.embeds:
                            try:
                                embed.set_image(url=url)
                            except:
                                pass
                        sent = await starboard_channel.send(
                            content=f"> {emoji} x{len(list)} **Posted in** {channel.mention} by "
                                    f"{message.author.mention}",
                            embed=embed)
                        id_dict = {}
                        i=1
                        for member in list:
                            id_dict[i] = member.id
                            i += 1
                        starrers = json.dumps(id_dict)
                        # SQLite doesn't work well with lists. So I dumped it into a json string
                        # to pull apart later.
                        message_tuple = (message.id, reaction.count, message.author.id, message.channel.id, sent.id, starrers)
                        await self.build_table(payload.guild_id, "messages", message_tuple)

                        # Get is used for custom emojis. If it returns none it isn't a custom one
                        # The second checks for regular emojis.
                        for guild in self.bot.guilds:
                            react = discord.utils.get(guild.emojis, name=config['starboard_config']['starred_react'])
                        if react is None:
                            react = config['starboard_config']['starred_react']
                        await message.add_reaction(react)

                        # These increment the stats for the various users.
                        for user in list:
                            if user.id != payload.user_id and not user.bot:
                                await self.increment_table(payload.guild_id,"leaderboard",user.id,"stars_given")

                        await self.increment_table(payload.guild_id,"leaderboard",message.author.id,"starred_messages")
                    # if the post is already on the starboard.
                    elif reaction.count > config['starboard_config']['threshold'] and already_posted:
                        # Gets the information for the DB for the message.
                        # To get data you have to use positional numbers from a list instead of dict.
                        # Message ID    star_number	    author_id	channel_id	  sb_Message_id     starrers
                        # 0	                1		        2		    3		        4               5
                        sql = f"""SELECT * FROM messages
                                WHERE id = {message.id}"""
                        star_message = await self.execute(sql,payload.guild_id,fetchone=True)
                        if str(payload.user_id) not in star_message[5]: # Get message then find who starred it.
                            await self.increment_table(payload.guild_id,"leaderboard",payload.user_id, "stars_given")
                            await self.increment_table(payload.guild_id,"messages",message.id, "star_number")

                            starrers_split = json.loads(star_message[5]) # Load JSON string into dict.
                            starrers_split[len(starrers_split)+1] = payload.user_id # Add new user to dict
                            starrers = json.dumps(starrers_split) # Dump to JSON string to use.
                            parameters = (starrers, message.id)

                            # SQLite doesn't work well with lists. So I dumped it into a json string
                            # to pull apart later.
                            await self.update_single_value_table(payload.guild_id,"messages","starrers", parameters)

                        else:
                            return
                        old_message = await starboard_channel.fetch_message(star_message[4])
                        for react in message.reactions:
                            if react.emoji == config['starboard_config']['star_react']:
                                # New in 2.0 instead of flatten.
                                list = [user async for user in react.users()]
                        new_content = f"> {emoji} x{len(list)}  **Posted in** {channel.mention} by {message.author.mention}"
                        await old_message.edit(content=new_content)
        except KeyError:
            raise KeyError('Starboard settings not initialised')


    @app_commands.command(name="my_starboard_stats")
    @commands.guild_only()
    async def my_stats(self, interaction: discord.Interaction, user: discord.Member = None):
        """Get yours or others stats from the starboard!"""
        if user is None:
            user = interaction.user
        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
        # Defer just in case things take a bit longer. Gives us up to 15 minutes to respond instead of 3s.
        await interaction.response.defer()
        guild = interaction.guild

        emoji = self.bot.get_emoji(config["starboard_config"]["star_react"])
        if emoji is None:
            emoji =  config["starboard_config"]["star_react"]
        # Starts building the embed.
        new_embed = discord.Embed(title=f':star: __**{user.display_name}\'s Starboard Stats**__ :star:',
                                  color=discord.Colour.gold())
        new_embed.set_author(name=guild.name, icon_url=guild.icon.url)
        new_embed.set_footer(text=f'Results provided by: {self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)

        # This gets the data for the messages for them to be searched.
        sql = f"""SELECT id, author_id, channel_id, star_number
                FROM messages
                ORDER BY star_number DESC;"""
        messages = await self.execute(sql,guild.id,fetchall=True)
        user_str = None
        rank = 1
        listing = ''
        for message in messages:
            if message[1] != user.id:
                continue
            channel = self.bot.get_channel(int(message[2]))
            message_object = await channel.fetch_message(int(message[0]))
            user_str = f'`[{str(rank)}.]` **{user.mention}\'s message in {channel.mention}:** \n' \
                   f'  {message[3]} {emoji}- \n' \
                   f'[Click to see message]({message_object.jump_url})'

            if rank <= 3:
                listing += f'{user_str}\n'
                rank += 1
            if rank > 3:
                break
        if user_str is None:
            listing = 'No Starred Messages'
        new_embed.add_field(name=f"{user.display_name}\'s Top Starred Messages", value=listing, inline=True)
        sql = f"""SELECT * FROM leaderboard
                WHERE id = {user.id}"""
        user_profile = await self.execute(sql, guild.id, fetchone=True)

        new_embed.add_field(name="Number of Self-Starred Posts:", value=f"{user_profile[3]}",
                            inline=False)
        new_embed.add_field(name="Number of Starred Messages:", value=f"{user_profile[2]}",
                            inline=False)
        new_embed.add_field(name="Number of Stars Given:", value=f"{user_profile[1]}", inline=False)
        await interaction.followup.send(embed=new_embed)

    @app_commands.command(name="leaderboard")
    @app_commands.choices(
        stat_table=[
            app_commands.Choice(name="Top Messages", value="messages"),
            app_commands.Choice(name="Top Users", value="leaderboard"),
        ])
    @commands.guild_only()
    async def leaderboard(self, interaction: discord.Interaction, stat_table:str):
        """Crab leaderboard! Pick from top messages or top users."""
        await interaction.response.defer()
        guild = interaction.guild

        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)

        emoji = self.bot.get_emoji(config["starboard_config"]["star_react"])
        if emoji is None:
            emoji = config["starboard_config"]["star_react"]
        if "messages" in stat_table:
            print(1)
            new_embed = discord.Embed(title=f':crab: __**Top Crabbed Messages**__ :crab:',
                                      color=discord.Colour.gold())
            new_embed.set_author(name=guild.name, icon_url=guild.icon.url)
            new_embed.set_footer(text=f'Results provided by: {self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            new_embed = discord.Embed(title=f':crab: __**Leaderboard**__ :crab:',
                                      color=discord.Colour.gold())
            new_embed.set_author(name=guild.name, icon_url=guild.icon.url)
            stat = 'star_number'
            sql = f"""SELECT id, author_id, channel_id, star_number
                    FROM messages
                    ORDER BY star_number DESC;"""
            messages = await self.execute(sql, guild.id, fetchall=True)
            print(2)
            rank = 1
            listing, list_message, f_name = '', '', ''
            for message in messages:

                channel = self.bot.get_channel(int(message[2]))
                message_object = await channel.fetch_message(int(message[0]))
                f_name = f'**Top Messages**'
                user_str = f'`[{str(rank)}.]` *{message_object.author.mention}\'s message in {channel.mention} ' \
                           f' :* **{message[3]} {emoji} - ' \
                           f'[Click to see message]({message_object.jump_url})**'
                if rank <= 5:
                    listing += f'{user_str}\n'
                    rank += 1
                if len(listing) > 900:
                    break
            new_embed.add_field(name=f_name,
                                value=listing,
                                inline=True)
            sql = """SELECT id, star_number
            FROM messages"""
            try:
                sb_stats = await self.execute(sql,guild.id,fetchall=True)
            except Exception as e:
                print(e)
                return
            print(sb_stats)
            star_number = 0
            for stat in sb_stats:
                star_number += stat[1]
            print(4)
            print(star_number)
            try:
                number_of_starred_messages = len(sb_stats)
            except Exception as e:
                print(e)
                return
            new_embed.set_footer(text=f'{number_of_starred_messages} messages have been crabbed with {star_number} '
                                      f'crabs',
                                 icon_url=self.bot.user.avatar.url)
            print(5)
        elif "leaderboard" in stat_table:
            new_embed = discord.Embed(title=f':crab: __**User Leaderboards**__ :crab:',
                                      color=discord.Colour.gold())
            new_embed.set_author(name=guild.name, icon_url=guild.icon.url)
            for stat in  ["stars_given", "starred_messages", "self_starred"]:
                if "stars_given" in stat:
                    title = "Crabs Given"
                elif "starred_messages" in stat:
                    title = "Crabbed Messages"
                elif "self_starred" in stat:
                    title = "Self Crabs"
                users = await self.search_top_value(guild.id, stat_table, stat)
                rank = 1
                listing, list_user, f_name, user_str = '', '', '', ''
                my_stat = None,
                for user in users:
                    list_user = self.bot.get_user(int(user[0]))
                    if list_user is None:
                        continue

                    else:
                        f_name = f'**{title}**'
                        user_str = f'`[{str(rank)}.]` *{list_user.display_name} :* **{user[1]}**'

                    if list_user == interaction.user:
                        my_stat = user_str
                        user_str = f'**\u27A4** {user_str} '
                    if rank <= 15:
                        listing += f'{user_str}\n'
                        rank += 1

                if my_stat is not None:
                    listing += f'\n__**Your Ranking:**__\n{my_stat}'

                sql = """SELECT * FROM leaderboard;"""
                sb_stats = await self.execute(sql, guild.id, fetchall=True)

                stat_counter = 0
                for user in sb_stats:
                    if "stars_given" in stat:
                        i = 1
                    elif "starred_messages" in stat:
                        i = 2
                    elif "self_starred" in stat:
                        i = 3
                    stat_counter += user[i]

                stats_count = len(sb_stats)

                new_embed.set_footer(
                    text=f'{stats_count} messages have been crabbed with {stat_counter} '
                         f'stars',
                    icon_url=self.bot.user.display_avatar.url)

                new_embed.add_field(name=f_name,
                                    value=listing,
                                    inline=True)

        await interaction.followup.send(embed=new_embed)

    @app_commands.command(name="create_star_db")
    @commands.is_owner()
    @commands.guild_only()
    async def create_star_db(self, interaction:discord.Interaction):
        """To add starboard database. Only use to initiate if error."""
        await interaction.response.send_message(embed=discord.Embed(title="Starting."))
        if os.path.isfile(f'config/{interaction.guild_id}/starboard.db'):
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
                os.remove(f'config/{interaction.guild_id}/starboard.db')
            else:
                await interaction.edit_original_response(embed=discord.Embed(title='Something went wrong.'))
                return
        elif not os.path.isfile(f'config/{interaction.guild_id}/starboard.db'):
            await interaction.edit_original_response(embed =discord.Embed(title="No Database Found. Creating New One"))
        sql = """CREATE TABLE IF NOT EXISTS leaderboard 
                    (id INTEGER PRIMARY KEY, 
                     stars_given INTEGER,
                     starred_messages INTEGER, 
                     self_starred INTEGER);"""
        await self.execute(sql, interaction.guild_id, commit=True)
        sql = """CREATE TABLE IF NOT EXISTS messages 
                    (id INTEGER PRIMARY KEY,
                    star_number INTEGER, 
                    author_id INTEGER, 
                    channel_id INTEGER,
                    sb_message_id INTEGER, 
                    starrers BLOB);"""
        await self.execute(sql, interaction.guild_id, commit=True)
        users = interaction.guild.members
        for user in users:
            if not user.bot:
                parameters = (user.id, 0, 0, 0)
                await self.build_table(interaction.guild_id, "leaderboard", parameters=parameters)

        await interaction.edit_original_response(embed=discord.Embed(title='Completed Database Build.', type="rich"))

    @app_commands.command(name="generatedata")
    @commands.is_owner()
    @commands.guild_only()
    async def generate(self, interaction: discord.Interaction):
        """Only used to generate testing data."""
        await interaction.response.defer()
        users = interaction.guild.members
        data = ("stars_given", "starred_messages", "self_starred" )
        for user in users:
            if not user.bot:
                await self.update_multiple_values_table(interaction.guild_id, "leaderboard", user.id, data, (random.randint(2, 40), random.randint(2, 40), random.randint(2, 40)))
        await interaction.followup.send(content="Done Generating User Data.")

    @app_commands.command(name="delete_user")
    @commands.is_owner()
    async def delete_user(self, interaction:discord.Interaction, user_id: str):
        """Use to remove a user from the starboard leaderboard."""
        user_id = int(user_id)

        sql = f"""SELECT 1 FROM leaderboard WHERE id = {user_id}"""
        data = await self.execute(sql,interaction.guild_id,fetchone=True)
        if not data:
            await interaction.response.send_message(
                embed=discord.Embed(title=f"Error querying the database. User did not exist in database."))
            return
        else:
            await self.rem_from_table(interaction.guild_id,"leaderboard", user_id)
            user = interaction.guild.get_member(user_id)
            await interaction.response.send_message(embed = discord.Embed(title=f"{user.name} "
                                                                          f"has been deleted from the database"))

            await interaction.response.send_message(
                embed=discord.Embed(title=f"User has been deleted from the database"))

    @app_commands.command(name="add_user")
    @commands.is_owner()
    @commands.guild_only()
    async def add_user(self, interaction:discord.Interaction, user_id: str):
        """Use to add a user to the starboard leaderboard."""
        user_id = int(user_id)
        sql = f"""SELECT 1 FROM leaderboard WHERE id = {user_id}"""
        data = await self.execute(sql, interaction.guild_id, fetchone=True)
        if data:
            await interaction.response.send_message(
                embed=discord.Embed(title=f"User already exists in the database."))
            return
        else:
            await self.build_table(interaction.guild_id, "leaderboard", (user_id, 0, 0, 0))

        try:
            user = interaction.guild.get_member(user_id)
            await interaction.response.send_message(embed=discord.Embed(title=f"{user.name} "
                                                                              f"has been added to the database"))
        except:
            await interaction.response.send_message(
                embed=discord.Embed(title=f"User has been added to the database"))

    async def search_top_value(self, guild_id:int, table:str, value: str):
        sql = f"""SELECT id,  {value}
        FROM {table}
        ORDER BY {value} DESC;"""

        return await self.execute(sql, guild_id, fetchall=True)

    async def build_table(self, guild_id:int, table: str, parameters: tuple):
        if "leaderboard" in table:
            sql = f"""
            INSERT INTO leaderboard (id,stars_given,starred_messages,self_starred) VALUES (?,?,?,?)
            ON CONFLICT(id) 
            DO UPDATE
            SET
            stars_given = excluded.stars_given,
            starred_messages = excluded.starred_messages,
            self_starred = excluded.self_starred
            WHERE
            excluded.stars_given > leaderboard.stars_given OR
            excluded.starred_messages > leaderboard.starred_messages OR
            excluded.self_starred > leaderboard.self_starred;
            """
        elif "message" in table:
            sql = """INSERT INTO messages (id, star_number, author_id, channel_id,sb_message_id, starrers) 
            VALUES (?,?,?,?,?,?)
            ON CONFLICT(id) 
            DO UPDATE
            SET
            star_number = excluded.star_number,
            starrers = excluded.starrers
            where
            excluded.star_number > messages.star_number;"""

        else:
            return


        await self.execute(sql, guild_id, parameters, commit=True)

    async def rem_from_table(self, guild_id:int,table: str, id:int):
        sql = f"""DELETE FROM {table} 
        WHERE id = {id}; """
        await self.execute(sql, guild_id, commit=True)

    async def update_multiple_values_table(self, guild_id:int, table:str, id:int, to_update: tuple, values:tuple):
        sql = f"""UPDATE {table}
        SET {to_update} = {values}
        WHERE id = {id};"""
        await self.execute(sql, guild_id, commit=True)

    async def update_single_value_table(self,  guild_id:int, table:str, to_update: str, parameters: tuple):
        sql = f"""UPDATE {table}
        SET {to_update} = ?
        WHERE id = ?;"""
        await self.execute(sql, guild_id, parameters, commit=True)


    async def increment_table(self, guild_id:int, table:str, id:int, to_update: str):
       sql = f"""UPDATE {table}
            SET {to_update} = {to_update} + 1
            WHERE id = {id}"""

       await self.execute(sql, guild_id, commit=True)

    async def execute(self, sql: str,guild_id:int, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        async with aiosqlite.connect(f'config/{guild_id}/starboard.db') as db:
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
    await bot.add_cog(Starboard(bot))
