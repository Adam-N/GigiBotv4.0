import asyncio
import json
import random
import requests
import discord
# from discord import app_commands
from discord.ext import commands

from lib.util import Util


class Friend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(name='nomean',aliases= ["yesmean"], description="For a friend who's being mean to themself!")
    async def nomean(self, ctx):
        """This command is for a friend who is being mean to themselves."""
        images = ["https://i.imgur.com/Q3mF2RV.jpg",
                  'https://cdn.discordapp.com/attachments/532380077896237061/791855065111592970/20200928_123113.jpg',
                  'https://media.discordapp.net/attachments/532380077896237061/1325510295338225814/FB_IMG_1736012065508.jpg?ex=677c0d29&is=677abba9&hm=da9c137977615b0c14b7cec0ec80385fa459a72aab0ab00b3416a9d3cab155c1&=&format=webp&width=670&height=670']

        embed = discord.Embed(color=0x00ff00)
        embed.title = "Don't be mean to yourself"
        embed.description = 'This is because we love you'
        embed.set_image(
            url=random.choice(images))
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='nosuck', aliases=["no_suck"], description="For friend's who think they suck.")
    async def nosuck(self, ctx):
        """For making your friend think twice saying they suck!"""
        embed = discord.Embed(color=0x00ff00)
        embed.title = "Don't be mean to yourself"
        embed.description = 'This is because we love you'
        embed.set_image(
            url='https://cdn.discordapp.com/attachments/532380077896237061/791855064804753418/fql8g0wcp1o51.jpg')
        await ctx.reply(embed=embed)

    @commands.hybrid_command(aliases=['hornyjail', 'nohorny', 'horny', 'yeshorny'],
                      description="For someone who's getting a little lewd.")
    async def horny_jail(self, ctx, jailee: discord.Member = None):
        """Send someone to horny jail..."""
        name = ""
        images = ["https://media.tenor.com/images/f781d9b1bbc4839dff9ad763c28deb46/tenor.gif",
                  "https://media1.tenor.com/images/6493bee2be7ae168a5ef7a68cf751868/tenor.gif?itemid=17298755",
                  "https://media.discordapp.net/attachments/767568459939708950/807751886278492170/no_horny.gif",
                  "https://media.discordapp.net/attachments/532380077896237061/1178765248782680135/bf0b002356302b24b8542f5ff786bd4a.png?ex=657755af&is=6564e0af&hm=3715e886ec791cab8ec567c2b9cf199ebd81e109fe52c7ce0522fa20bcdc681b&=&width=478&height=670"]
        url = random.choice(images)
        if jailee is not None:
            if jailee.nick:
                name = " " + jailee.nick

            else:
                name = " " + jailee.display_name
        embed = discord.Embed(color=0x00ff00)
        embed.title = "You're gross!"
        embed.description = f'This is for your own good{name}!'
        embed.set_image(url=url)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(description="For someone who needs sleep!")
    async def sleep(self, ctx, member: discord.Member = None):
        """This command is meant to tell a friend to go to sleep!"""
        name = ""
        images = ["https://media1.tenor.com/images/f3fd2914f8db39338263dc7b657bcb43/tenor.gif?itemid=5219925",
                  "https://media1.tenor.com/images/5fb8a2a7db6ce0715013d870631ab81f/tenor.gif?itemid=6146952",
                  "https://media1.tenor.com/images/0e19c69eb1d0e6d58f1c8418b8232881/tenor.gif?itemid=15301397",
                  "https://media.tenor.com/images/11baf16c4029abc97bdae7ff3f6ffe3b/tenor.gif",
                  "https://media.giphy.com/media/rvxGjhW3TKVeo/source.gif",
                  "https://i.gifer.com/RLil.gif",
                  "https://i.imgur.com/juYkVr8.jpg",
                  "https://cdn.discordapp.com/attachments/586181879611260928/850529213000712233/tenor.gif"]
        url = random.choice(images)
        embed = discord.Embed(color=0x00ff00)
        if member is not None:
            if member.nick:
                name = " " + member.nick

            else:
                name = " " + member.display_name
        embed.title = f"Go to sleep{name}!"
        embed.description = 'This is for your own good!'
        embed.set_image(url=url)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(description="For someone who needs sleep!")
    async def terry(self, ctx):
        """Summon the one true God of Thumbs"""
        name = ""
        images = ["https://i.imgur.com/rq4Om02.jpg", "https://i.imgur.com/9c5GchZ.jpg",
                  "https://i.imgur.com/9c5GchZ.jpg", "https://i.imgur.com/4XYABRg.jpg",
                  "https://i.imgur.com/VK0vDv8.jpg", "https://i.imgur.com/C4p4pmN.jpg",
                  "https://i.imgur.com/AcwdkGU.jpg", "https://i.imgur.com/yiYEgmu.png",
                  "https://i.imgur.com/8Wu8voN.jpg", "https://i.imgur.com/81e3EGg.jpg",
                  "https://i.imgur.com/5hnKRzL.jpg", "https://i.imgur.com/zpYv6fT.jpg",
                  "https://i.imgur.com/W5Pg7d3.png", "https://i.imgur.com/o14epCZ.png",
                  "https://i.imgur.com/5YkAqrs.png", "https://i.imgur.com/sTFehUh.jpg",
                  "https://i.imgur.com/MJu4EVZ.png", "https://i.imgur.com/XUTsIDg.png",
                  "https://i.imgur.com/OjjwX4h.jpg", "https://i.imgur.com/2ITAMQ4.jpg"]
        url = random.choice(images)
        embed = discord.Embed(color=0x00ff00)

        embed.title = f"You have summoned the one true god of thumbs!"
        embed.description = ' '
        embed.set_image(url=url)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="credits", description="Shows dev credits.")
    async def credits(self, ctx):
        """Shows the credits for the bot."""
        embed = discord.Embed(title='Development Credits',
                              description='Thank you to all of the following folks for making Gigi possible.',
                              colour=0xffff33)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name='Developers', value='ShiinaBat#8227\nAdam.M#9788\nInf_Wolf14#7391', inline=True)
        embed.add_field(name='Producers', value='Element#1337\nIlyesia#8008')
        embed.add_field(name='Alpha Testers',
                        value='AzureEiyu#9781, Isaac2K#1948, Kurokaito#5489, Vyxea#0001',
                        inline=False)
        embed.add_field(name='Character Designer',
                        value='[NEBULArobo](https://nebularobo.carrd.co/)', inline=False)
        embed.add_field(name='Icon Artist',
                        value='[crankiereddy](https://twitter.com/crankiereddy)',
                        inline=False)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="dadjoke", description="Dad Jokes")
    async def dad_joke(self, ctx):
        """Sends a dad joke."""
        if await Util.check_channel(ctx, True):
            headers = {"Accept": "text/plain"}
            url = "https://icanhazdadjoke.com/"
            response = requests.request("GET", url, headers=headers)
            await ctx.send(f'`{response.text}`')
        else:
            await ctx.message.delete()

    @commands.hybrid_command(aliases=["XIV", "freetrial", "free_trial"], description="Did you know...")
    async def xiv(self, ctx):
        """Did you know....."""
        chance = 90
        if random.randint(1, 100) < chance:
            embed = discord.Embed(color=0xe74c3c)
            embed.title = f"Have you heard?"
            embed.description = ' '
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/532380077896237061/1134934711542747206/image.jpg")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(color=0x7289da)

            embed.title = f"Have you heard?"
            embed.description = 'Did uwu know thawt the cwiticawwy accwaimed MMOWPG finaw fantasy xiv has a fwee ' \
                                'twiaw, awnd incwudes the entiwety of A Weawm Webown AWND the awawd-winning ' \
                                'Heavenswawd expansion and stwomblood up tuwu wevew 70 with no westwictions on ' \
                                'pwaytime? sign up, awnd enjoy Eowzea today!  Now on xbawks! :3 '
            await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Friend(bot))