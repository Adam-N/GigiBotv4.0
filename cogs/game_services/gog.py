from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import discord
import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement

from cogs.game_services.utils import already_posted

if TYPE_CHECKING:
    from collections.abc import Generator

    from bs4.element import NavigableString, PageElement


def create_embed(
    server_id: str,
    game_name: str = "",
    image_url: str = "",
    game_url: str = "",
    *,
    no_claim: bool = False,
) -> discord.Embed:
    """Create the embed that we will send to Discord.

    Args:
        server_id: ID of the server.
        game_name: The game name.
        game_url: URL to the game.
        image_url: Game image.
        no_claim: Don't use https://www.gog.com/giveaway/claim

    Returns:
        Embed: The embed we will send to Discord.
    """
    if not game_name:
        game_name = "GOG Giveaway"

    if not game_url:
        game_url = "https://www.gog.com/"

    description: str = (
        f"[Click here to claim {game_name}!](https://www.gog.com/giveaway/claim)"
    )

    if no_claim:
        description = (
            f"[Click here to claim {game_name}!]({game_url})"
        )

    embed = discord.Embed(description=description)
    embed.set_author(name=game_name, url=game_url, icon_url="https://cdn.discordapp.com/attachments/767568459939708950/"
                                                            "1353202070177447978/latest.png?ex=67e0cb22&is=67df79a2&hm="
                                                            "07a61775131c70b30d84c7a442849c716968988e824d01f7e9f379"
                                                            "fa681588a3&")
    if image_url:
        image_url = image_url.removesuffix(",")

        if image_url.startswith("//"):
            image_url = f"https:{image_url}"

        embed.set_image(url=image_url)

    with open(f'config/{server_id}/free_games/gog.txt', 'a') as f:
        f.write(f"{game_name}\n")
    return embed


def get_free_gog_game_from_store(server_id: str) -> Generator[discord.Embed | None, Any, None]:
    """Check if free GOG game from games store.

    Yields:
        discord.Embed: Embed for the free GOG games.
    """
    request: requests.Response = requests.get(
        "https://www.gog.com/en/games?priceRange=0,0&discounted=true",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        },
        timeout=30,
    )
    soup = BeautifulSoup(request.text, "html.parser")

    games: PageElement | Tag | NavigableString | None = soup.find("div", {"selenium-id": "paginatedProductsGrid"})

    if games is None:
        logging.info("GOG: No free games found")
        return

    if not hasattr(games, "children"):
        logging.info("GOG: No free games found")
        return

    for child in games.children:  # type: ignore  # noqa: PGH003
        if not hasattr(child, "attrs"):
            continue

        # Game name
        game_class = child.find("div", {"selenium-id": "productTileGameTitle"})  # type: ignore  # noqa: PGH003
        game_name = game_class["title"]  # type: ignore  # noqa: PGH003
        if already_posted(server_id, "gog", game_name):
            logging.info(f"Game already posted: {game_name}")
            continue

        # Game URL
        game_url = child.find("a", {"class": "product-tile--grid"})["href"]  # type: ignore  # noqa: PGH003
        logging.info(f"{game_name}: Game URL: {game_url}")

        # Game image
        image_url_class: Tag | NavigableString | None = child.find(  # type: ignore  # noqa: PGH003
            "source",
            attrs={"srcset": True},
        )
        if hasattr(image_url_class, "attrs"):
            images: list[str] = image_url_class.attrs["srcset"].strip().split()  # type: ignore  # noqa: PGH003
            image_url: str = f"{images[0]}"
        else:
            image_url = ""

        yield create_embed(
            server_id=server_id,
            game_name=game_name,
            game_url=game_url,
            image_url=image_url,
            no_claim=True,
        )


def get_giveaway_link(giveaway: PageElement | Tag | NavigableString | None, game_name: str) -> str:
    """Get the giveaway link from the GOG giveaway.

    Args:
        giveaway: The giveaway tag.
        game_name: The game name.

    Returns:
        The giveaway link. Defaults to https://www.gog.com/ if not found.
    """
    gog_giveaway_link: Tag | NavigableString | int | None = giveaway.find("a", {"selenium-id": "giveawayOverlayLink"})  # type: ignore  # noqa: PGH003
    if not hasattr(gog_giveaway_link, "attrs"):
        logging.error(f"{game_name}: No giveaway link found on GOG for {game_name} because it's doesn't have 'attrs'", giveaway)
        return "https://www.gog.com/"

    # Only allow Tag
    if not isinstance(gog_giveaway_link, Tag):
        logging.error(f"{game_name}: No giveaway link found on GOG for {game_name} because it's not a 'Tag'", giveaway)
        return "https://www.gog.com/"

    giveaway_link = str(gog_giveaway_link.attrs["href"])
    return giveaway_link


def get_game_image(giveaway: BeautifulSoup, game_name: str) -> str:
    """Get the game image from the GOG giveaway.

    Args:
        giveaway: The giveaway tag.
        game_name: The game name.

    Returns:
    The game image URL. Defaults to a placeholder image if not found.
    """
    default_image = "https://images.gog.com/86843ada19050958a1aecf7de9c7403876f74d53230a5a96d7e615c1348ba6a9.webp"

    # Game image
    image_url_class: Tag | NavigableString | None = giveaway.find(
        "source",
        attrs={"srcset": True},  # type: ignore  # noqa: PGH003
    )

    # If no image URL, return an empty list
    if image_url_class is None:
        logging.error(f"{game_name}: No image URL found on GOG for {game_name}",
            giveaway,
        )
        return default_image

    # Check if image_url_class has attrs
    if not hasattr(image_url_class, "attrs"):
        logging.error(f"{game_name}: No attrs found on GOG for {game_name}", giveaway)
        return default_image

    images: list[str] = image_url_class.attrs["srcset"].strip().split()  # type: ignore  # noqa: PGH003
    image_url = images[0]

    if not image_url:
        logging.error(f"{game_name}: No image URL found on GOG for {game_name}", giveaway)
        return default_image

    return image_url


def get_game_name(giveaway_soup: BeautifulSoup, giveaway: PageElement | Tag | NavigableString | None) -> str:
    """Get the game name from the GOG giveaway.

    Args:
        giveaway_soup: The giveaway tag.
        giveaway: The giveaway tag.

    Returns:
        The game name. Defaults to "GOG Giveaway" if not found.
    """
    img_tag: PageElement | Tag | NavigableString | None = giveaway_soup.find("img", alt=True)
    if not hasattr(img_tag, "attrs"):
        logging.error("No img tag found on GOG for game", giveaway)
        return "GOG Giveaway"

    # Extract the game name from the alt attribute
    if img_tag and isinstance(img_tag, Tag):
        game_name_alt: str | list[str] = img_tag["alt"]
        if isinstance(game_name_alt, str) and game_name_alt:
            game_name: str = game_name_alt.replace(" giveaway", "") if img_tag else "Game name not found"
        if isinstance(game_name_alt, list) and game_name_alt:
            game_name = game_name_alt[0].replace(" giveaway", "") if img_tag else "Game name not found"
            logging.warning(f"{game_name}: was a list of strings so could be wrong?")
    else:
        game_name = "GOG Giveaway"
        logging.error(f"{game_name}: No img tag found on GOG for {game_name}", img_tag)

    return game_name


def get_free_gog_game(server_id: str) -> discord.Embed | None:
    """Check if free GOG game.

    Returns:
        DiscordEmbed: Embed for the free GOG games.
    """

    request: requests.Response = requests.get(
        "https://www.gog.com/",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        },
        timeout=30,
    )

    soup = BeautifulSoup(request.text, "html.parser")
    giveaway: PageElement | Tag | NavigableString | None = soup.find("giveaway")
    giveaway_soup: BeautifulSoup = BeautifulSoup(str(giveaway), "html.parser")

    if giveaway is None:
        return None

    # Get the game name
    game_name: str = get_game_name(giveaway_soup=giveaway_soup, giveaway=giveaway)

    if already_posted(server_id,"gog", game_name):
        return None

    giveaway_link: str = get_giveaway_link(giveaway=giveaway, game_name=game_name)
    image_url: str = get_game_image(giveaway=giveaway_soup, game_name=game_name)

    # Create the embed and add it to the list of free games.
    return create_embed(
        server_id=server_id,
        game_name=game_name,
        game_url=giveaway_link,
        image_url=image_url,
    )
