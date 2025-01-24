import json
import os
import datetime as dt
import discord
import pytz
from discord import app_commands
from discord.ext import tasks, commands
from discord.errors import NotFound


class LFGCog(commands.Cog, name='lfg'):
    """LFG Rules"""

    def __init__(self, bot):
        self.bot = bot
        self.lfg_message.start()

    def cog_unload(self):
        self.lfg_message.cancel()

    @app_commands.command(name="lfg_config")
    @commands.is_owner()
    async def lfg_config(self, interaction: discord.Interaction):
        lfg_config = {
            'dtg_lfg': interaction.channel.id,
            'bot_channel':interaction.channel.id,
            'bot_user': 1
        }
        if os.path.isfile(f'config/{interaction.guild_id}/config.json'):
            with open(f'config/{interaction.guild_id}/config.json', 'r') as f:
                config = json.load(f)
        config['lfg_config'] = lfg_config
        with open(f'config/{interaction.guild_id}/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        await interaction.response.send_message(embed=discord.Embed(title=f'LFG config initialized'))

    @tasks.loop(minutes=30)
    async def lfg_message(self):
        try:
            guild = self.bot.get_guild(**GUILD ID HERE**)
            if os.path.isfile(f'config/{guild.id}/config.json'):
                with open(f'config/{guild.id}/config.json', 'r') as f:
                    config = json.load(f)

                lfg_bot = self.bot.get_user(int(config["lfg_config"]["bot_user"]))
                channel = self.bot.get_channel(int(config["lfg_config"]["dtg_lfg"]))
                bot_channel = self.bot.get_channel(int(config["lfg_config"]["bot_channel"]))

                try:
                    last_message = await channel.fetch_message(channel.last_message_id)
                except NotFound:
                    messages = [message async for message in channel.history(limit=4)]
                    for message in messages:
                        try:
                            last_message = message
                            break
                        except:
                            continue
                if last_message.author.bot:
                    return
                if last_message.created_at + dt.timedelta(minutes=360) <= discord.utils.utcnow():
                    tags = []
                    role_string = ", "
                    for role in guild.roles:
                        if "D2" in role.name:
                            tags.append(role.mention)
                    role_string = role_string.join(tags)

                    embed = discord.Embed(title="**Welcome to the LFG Channel!**",
                                          description="Here's a few tips to help you get the most out of this "
                                                      "channel and successfully find folks to play with.")

                    embed.add_field(name="**1. Tag Usage**",
                                    value="The best way to draw attention to your LFG is to use the appropriate role "
                                          "tag. This will send a notification directly to folks who are interested in "
                                          "that type of content. Please be patient and allow at least 10-15 minutes "
                                          "for a response before searching through other means or giving the spot "
                                          "away. Please limit yourself to the tag for the content you are looking to "
                                          "play.", inline=False)

                    embed.add_field(name="**2. Scheduling LFGs**",
                                    value=" We're an adult community so many of our members have limited "
                                          "playtime due to real life responsibilities. Therefore, you can "
                                          "ensure a better turn out for your LFG by planning it in advance "
                                          "and advertising it within this channel. Use  '/event create'"
                                          f" in the {bot_channel.mention} and follow "
                                          f"the prompts from {lfg_bot.mention} "
                                          "to create your own interactive LFG!", inline= False)
                    embed.add_field(name="**3. Requirements and Etiquette**",
                                    value="Please respect everyone's time. This means being upfront with any "
                                          "requirements (experienced only, teaching run, etc.), joining an LFG only "
                                          "if you meet the requirements, being punctual or communicating immediately "
                                          "if you'll be late or can't make it, and filling empty spots from the "
                                          "tentative list first before opening them to others.", inline=False)
                    embed.add_field(name="Appropriate Tags:", value=f"{role_string}")

                else:
                    return
                try:
                    async for message in channel.history(limit=40):
                        if message.author == self.bot.user:
                            await message.delete()
                            break
                except:
                    pass
                await channel.send(embed=embed)
        except AttributeError:
            pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LFGCog(bot))
