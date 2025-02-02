import discord
from discord import app_commands
from discord.ext import commands
import datetime as dt

from discord.ext.commands import has_permissions

from lib.util import Util


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_db = None

    @app_commands.command()
    @commands.guild_only()
    async def joined(self, interaction: discord.Interaction, member: discord.Member = None):
        """Says when a member joined."""
        ctx = await self.bot.get_context(interaction)
        if await Util.check_channel(ctx, True):
            if member is None:
                member = ctx.author
            await ctx.send(
                f'{member.display_name} joined at {dt.datetime.strftime(member.joined_at, "%H:%M %b %dth %Y")}.'
                f' That\'s {Util.deltaconv(int((discord.utils.utcnow() - member.joined_at).total_seconds()))}'
                f' ago!')

    @app_commands.command(name='top_role')
    @commands.has_permissions(manage_permissions=True)
    @commands.guild_only()
    async def show_toprole(self, interaction: discord.Interaction, member: discord.Member = None):
        """Simple command which shows the members Top Role."""
        ctx = await self.bot.get_context(interaction)
        if await Util.check_channel(ctx, True):
            if member is None:
                member = ctx.author
            await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    @app_commands.command(name='perms')
    @commands.has_permissions(manage_permissions=True)
    @commands.guild_only()
    async def check_permissions(self, interaction: discord.Interaction, member:discord.Member):
        """A simple command which checks a members Guild Permissions."""
        ctx = await self.bot.get_context(interaction)
        if await Util.check_channel(ctx, True):
            perms = '\n'.join(perm for perm, value in member.guild_permissions if value)
            embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
            embed.set_author(icon_url=member.avatar.url, name=str(member))
            embed.add_field(name='\uFEFF', value=perms)
            await ctx.send(content=None, embed=embed)

    @app_commands.command(name="check")
    @commands.has_permissions(manage_permissions=True)
    @commands.guild_only()
    async def check(self, interaction: discord.Interaction, member: discord.Member):
        """Get info about a user."""
        ctx = await self.bot.get_context(interaction)
        if await Util.check_channel(ctx, True):
            embed = discord.Embed(title=f"{member.name}'s Profile", description="Check this out")
            embed.add_field(name="Joined:",
                            value=f"{Util.deltaconv(int((discord.utils.utcnow() - member.joined_at).total_seconds()))} ago")
            embed.add_field(name="Created on", value=f"{dt.datetime.strftime(member.created_at, '%d %B, %Y  %H:%M')}")
            embed.add_field(name="Username", value=f"{member.name}{member.discriminator}")
            embed.add_field(name="Top role:", value=f"{member.top_role}")
            embed.set_thumbnail(url=member.avatar.url)
            await ctx.send(embed=embed)

    @app_commands.command(name="echo")
    @commands.guild_only()
    @commands.is_owner()
    async def echo(self, interaction: discord.Interaction, channel:discord.TextChannel, message: str):
        await channel.send(message)
        await interaction.response.send_message(f"Message sent to {channel.name}. It says {message}", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mod(bot))
