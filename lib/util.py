import os
import json
import discord
from discord import channel

class Util:
    def __init__(self):
        self.server_db = None

    @staticmethod
    def sing(amount, unit):
        """singularizer(?) - returns a string containing the amount
        and type of something. The type/unit of item will be pluralized
        if the amount is greater than one."""
        return f"{amount} {amount == 1 and f'{unit}' or f'{unit}s'}"

    @staticmethod
    def deltaconv(seconds):
        """Converts a timedelta's total_seconds() to a humanized string."""
        mins, secs = divmod(seconds, 60)
        hrs, mins = divmod(mins, 60)
        dys, hrs = divmod(hrs, 24)
        mts, dys = divmod(dys, 30)
        yrs, mts = divmod(mts, 12)
        timedict = {'year': yrs, 'month': mts, 'day': dys, 'hour': hrs, 'minute': mins, 'second': secs}
        cleaned = {k: v for k, v in timedict.items() if v != 0}
        return " ".join(Util.sing(v, k) for k, v in cleaned.items())

    @staticmethod
    async def check_channel(ctx, bot_exclusive: bool = None):
        if not os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            await Util.reset_config(ctx)
        with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
            config = json.load(f)
        channel = ctx.channel
        if bot_exclusive:
            try:
                if channel.type is discord.ChannelType.text:
                    if channel.id not in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __only__ available in bot channels!'), delete_after=5)
                        return False
                elif channel.type is discord.ChannelType.private_thread or \
                        channel.type is discord.ChannelType.public_thread:
                    if ctx.parent_id not in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __only__ available in bot channels!'), delete_after=5)
                        return False
            except AttributeError:
                if ctx.channel.type is discord.ChannelType.text:
                    if ctx.id not in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __only__ available in bot channels!'), delete_after=5)
                        return False
                elif ctx.type is discord.ChannelType.private_thread or \
                        ctx.type is discord.ChannelType.public_thread:
                    if ctx.parent_id not in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __only__ available in bot channels!'), delete_after=5)
                        return False

        elif bot_exclusive is not None:
            try:
                if channel.type is discord.ChannelType.text:
                    if channel.id in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __NOT__ available in bot channels!'), delete_after=5)
                        return False
                elif channel.type is discord.ChannelType.private_thread or \
                        channel.type is discord.ChannelType.public_thread:
                    if channel.parent_id in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __NOT__ available in bot channels!'), delete_after=5)
                        return False
            except AttributeError:
                if channel.type is discord.ChannelType.text:
                    if channel.id in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __NOT__ available in bot channels!'), delete_after=5)
                        return False
                elif channel.type is discord.ChannelType.private_thread or \
                        channel.type is discord.ChannelType.public_thread:
                    if channel.parent_id in config['channel_config']['bot_channels']:
                        await ctx.reply(embed=discord.Embed(title='This command is __NOT__ available in bot channels!'), delete_after=5)
                        return False

        return True

    @staticmethod
    async def check_exp_blacklist(ctx):
        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            with open(f'config/{ctx.guild.id}/config.json', 'r') as f:
                config = json.load(f)
            if ctx.channel.id in config['channel_config']['exp_blacklist']:
                return False
            return True
        else:
            await ctx.reply(embed=discord.Embed(title='**[Error]** : Server config not initialized',
                                               description='Please run initialization'))
            return

    """    async def reset_user_flags(self, ctx):
        self.server_db = self.db[str(ctx.guild.id)]['users']
        reset_flags = {'flags': {'daily': True, 'daily_stamp': discord.utils.utcnow(), 'thank': True}}
        for member in ctx.guild.members:
            if not member.bot:
                self.server_db.find_one_and_update({"_id": str(member.id)}, {'$set': reset_flags})
                self.server_db.find_one_and_update({'_id': str(member.id)}, {'$set':
                    {'gold.daily_count': 0}})"""

    @staticmethod
    async def reset_config(ctx):
            # Has to have 1s in things as it throws errors when trying to add things while they are null.
        config = {
            'prefix': '*',
            'channel_config': {
                'config_channel': ctx.channel.id,
                'modlog_channel': ctx.channel.id,
                'welcome_channel': ctx.channel.id,
                'lounge': ctx.channel.id,
                "guild_channel": ctx.channel.id,
                "support_channel": ctx.channel.id,
                'bot_channels': [],
            },
            'role_config': {
                'posse': 1,
                'triumphant': 1,
                'birthday': 1,
            },
            "starboard_config": {
                "starboard_channel": ctx.channel.id,
                "star_react": "\uD83E\uDD80",
                "starred_react": "<a:crab_rave:588599353590022154>",
                "threshold": 3
            },
            "triumphant_config": {
                "triumph_channel": ctx.channel.id,
                "triumph_react": "\ud83c\udf96\ufe0f"
            }
        }

        if os.path.isfile(f'config/{ctx.guild.id}/config.json'):
            os.remove(f'config/{ctx.guild.id}/config.json')
        with open(f'config/{ctx.guild.id}/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        await ctx.reply(embed=discord.Embed(title=f'Default server config set'))
