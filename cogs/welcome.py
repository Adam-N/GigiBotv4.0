import json
import discord
from discord.ext import commands

from cogs.profile import Profile
import datetime as dt


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await Profile.add_profile(Profile(self.bot), member.guild.id, member)

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        await Profile.del_profile(Profile(self.bot), payload.guild_id, payload.user)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        with open(f'config/{before.guild.id}/config.json', 'r') as f:
            config = json.load(f)
        welcome_role = before.guild.get_role(config['role_config']['posse'])
        welcome_channel = self.bot.get_channel(config['channel_config']['lounge'])
        guild_channel = self.bot.get_channel(config['channel_config']['guild_channel'])
        support_channel = self.bot.get_channel(config['channel_config']['support_channel'])

        if welcome_role not in before.roles and welcome_role in after.roles and before.joined_at > discord.utils.utcnow() - dt.timedelta(minutes=20):

            await welcome_channel.send(content=f"**Welcome to GOLDxGUNS**, {after.mention}! :ggwavea: \n \n"
                                               f"Here's a couple things you can do to get started:\n"
                                                f"> **1.** Check out our <id:guide> \n"
                                                f"> **2.** Pick up LFG roles in <id:customize>\n"
                                                f"> **3.** Customize your channels in <id:browse>\n"
                                                f"> **4.** Join one of {guild_channel.mention}\n \n"
                                                f"**If you need any help then let us know in** {support_channel.mention}!")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
