import os
import json
import asyncio

import discord
from discord.ext import commands



def get_prefix(bot, message):
    try:
        if os.path.isfile(f'config/{str(message.guild.id)}/config.json'):
            with open(f'config/{str(message.guild.id)}/config.json', 'r') as f:
                config = json.load(f)
            prefixes = [config['prefix']]
        else:
            prefixes = ['*']
        return prefixes
    except:
        return ['*']



initial_cogs = ["master", "cogs.friend", "cogs.mod", "cogs.starboard"]

bot = commands.Bot(command_prefix=get_prefix, description='A bot designed for GoldxGuns', intents=discord.Intents.all(),
                   slash_commands=True)

async def main():
    await bot.login(token=token)
    await bot.connect()


#async def change_presence():
#    game = discord.Game("help for more information")
#    await bot.change_presence(status=discord.Status.idle, activity=game)

@bot.command(hidden=True)
@commands.is_owner()
async def sync(ctx):
    message = await ctx.send(f"Syncing...")
    synced = await bot.tree.sync()
    await message.edit(content=f"Synced {len(synced)} command(s).")

@bot.command(hidden=True)
@commands.is_owner()
async def close(ctx):
    await bot.close()

@bot.event
async def setup_hook():
    print("This is your set up running")
    for guild in bot.guilds:
        if not os.path.isdir(f'config/{guild.id}/'):
            os.makedirs(f'config/{guild.id}/')
    for extension in initial_cogs:
        await bot.load_extension(extension)
        print(extension)

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')
    print(f'Successfully logged in and booted...!')
    game = discord.Game(";help for more information")
    await bot.change_presence(status=discord.Status.idle, activity=game)

"""@bot.event
async def on_error(event, *args, **kwargs):
    config_channel = await bot.fetch_channel(590014505753509888)
    message = event.message
    if os.path.isfile(f'config/{str(message.guild.id)}/config.json'):
        with open(f'config/{str(message.guild.id)}/config.json', 'r') as f:
            config = json.load(f)
        config_channel = await bot.fetch_channel(config['channel_config']['config_channel'])
    else:
        return
    new_embed = discord.Embed(title=f'**[Error]** {type(event).__name__} **[Error]**')
    new_embed.add_field(name="Event", value=f"{args}")
    if kwargs:
        new_embed.add_field(name="Arguments", value=f"{kwargs}")
    await config_channel.send(embed=new_embed)"""


print('\nLoading token and connecting to client...')
token = open('token.txt', 'r').readline()
# schedule.add_job(monthly, 'cron', month='*', day='1')
asyncio.run(main())
