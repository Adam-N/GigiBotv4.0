from __future__ import annotations

import os


def already_posted(server_id: str, service: str, game_name: str) -> bool:
    """Check if the game has already been posted.

    Args:
        server_id: id of the server being posted in.
        service: The game service to search.
        game_name: The game name, we check if this is in the file.

    Returns:
        bool: True if already has been posted.
    """
    if os.path.isfile(f'config/{server_id}/free_games/{service}.txt'):
        with open(f'config/{server_id}/free_games/{service}.txt', 'r') as f:
            if game_name in f.read():
                return True

    return False