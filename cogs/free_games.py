from __future__ import annotations

import json
import logging
import os.path

from discord.ext import commands, tasks

from cogs.game_services.gog import get_free_gog_game_from_store
from cogs.game_services.steam import get_free_steam_games
from cogs.game_services.epic import get_free_epic_games


class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_games.start()

    def cog_unload(self):
        self.send_games.cancel()

    @tasks.loop(hours = 8)
    async def send_games(self):
        for server in self.bot.guilds:
            server_id = str(server.id)
            with open(f'config/{str(server.id)}/config.json', 'r') as f:
                config = json.load(f)

            posting_channel = server.get_channel(config["channel_config"]["free_game_channel"])
            try:
                for game in get_free_steam_games(server_id):
                    await posting_channel.send(embed=game)

            except Exception as e:
                logging.error(f"Error when checking Steam for free games: {e}")

            try:
                for game in get_free_epic_games(server_id):
                    await posting_channel.send(embed=game)

            except Exception as e:
                msg: str = f"Error when checking Epic for free games: {e}"
                logging.error(msg)

            try:
                for game in get_free_gog_game_from_store(server_id):
                   await posting_channel.send(embed=game)

            except Exception as e:
               logging.error(f"Error when checking GOG (search page) for free games: {e}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FreeGames(bot))
