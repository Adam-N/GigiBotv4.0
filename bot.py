import os
import json
import asyncio

import discord
from discord.ext import commands

from cogs.drive import Drive


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


initial_cogs = ["master", "cogs.friend", "cogs.mod", "cogs.starboard", "cogs.profile", "cogs.triumphant", "cogs.drive"]

bot = commands.Bot(command_prefix=get_prefix, description='A bot designed for GoldxGuns', intents=discord.Intents.all(),
                   slash_commands=True)

async def main():
    await bot.login(token=token)
    await bot.connect()


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
        print(f"{extension} Loaded")

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')
    print(f'Successfully logged in and booted...!')
    game = discord.Game(";help for more information")
    await bot.change_presence(status=discord.Status.idle, activity=game)

async def weekly():
    """Weekly reset timer"""
    for guild in bot.guilds:
        if os.path.isfile(f'config/{str(guild.id)}/config.json'):
            with open(f'config/{str(guild.id)}/config.json', 'r') as f:
                config = json.load(f)
        if config['channel_config']['config_channel']:
            config_channel = bot.get_channel(config['channel_config']['config_channel'])
            # Weekly Reset Functions Here
            await triumphant_reset(guild)
            await config_channel.send(embed=discord.Embed(title=f'{config_channel.guild.name} Weekly Reset!'))

async def triumphant_reset(server):
    # This resets the triumphant for the week.
    with open(f'config/{server.id}/config.json', 'r') as f:
        config = json.load(f)
    chan = bot.get_channel(int(config['triumphant_config']["triumph_channel"]))
    config_channel = bot.get_channel(config['channel_config']['config_channel'])

    await config_channel.send('Starting Weekly Reset')

    if os.path.isfile(f'config/{server.id}/triumphant_copy.json'):
        os.remove(f'config/{server.id}/triumphant_copy.json')
    with open(f'config/{server.id}/triumphant.json', 'r') as f:
        users = json.load(f)

    with open(f'config/{server.id}/triumphant_copy.json', 'w') as f:
        json.dump(users, f)

    os.remove(f'config/{server.id}/triumphant.json')

    triumphant = {}

    with open(f'config/{str(server.id)}/triumphant.json', 'w') as f:
        json.dump(triumphant, f)
    try:
        await Drive.weekly_reminder(Drive(bot), server.id)
    except:
        pass
    try:
        await Drive.create(Drive(bot))
    except:
        pass
    reset_embed = discord.Embed(title="\U0001f5d3| New Week Starts Here. Get that bread!")
    await chan.send(embed=reset_embed)

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
