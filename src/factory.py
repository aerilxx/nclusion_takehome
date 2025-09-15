import asyncio
import logging
from typing import Dict, Optional
from .models import Game, Player, Status, PlayerStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameFactory:
    def __init__(self):
        self._games: Dict[int, Game] = {}
        self._next_id = 1
        self._lock = asyncio.Lock()

    async def create_game(self, name: str) -> Game:
        async with self._lock:
            game_id = self._next_id
            self._next_id += 1
            logging.info(f"create game {name} for {game_id} time")
            game = Game(id=game_id, name=name, status=Status.PENDING)
            self._games[game_id] = game
        return game

    async def get_game(self, game_id: int) -> Optional[Game]:
        async with self._lock:
            return self._games.get(game_id)
    
    async def remove_game(self, game_id: int) -> bool:
        """Remove a game from the factory. Returns True if game was removed, False if not found."""
        async with self._lock:
            return self._games.pop(game_id, None) is not None
    
    async def get_all_games(self) -> list[Game]:
        """Get all games. Returns a copy of the games list for thread safety."""
        async with self._lock:
            return list(self._games.values())
    
    async def get_game_count(self) -> int:
        """Get the total number of games."""
        async with self._lock:
            return len(self._games)



class PlayerFactory:
    def __init__(self):
        self._players: Dict[str, Player] = {}
        self._lock = asyncio.Lock()

    # Note: Using asyncio.Lock for thread safety in async context
    
    async def get_or_create_player(self, player_id: str, email: Optional[str], name: Optional[str]) -> Player:
        async with self._lock:
            if player_id in self._players:
                return self._players[player_id]
            player = Player(id=player_id, email=email, name=name, stats=PlayerStats())
            self._players[player_id] = player
            return player

    async def get_player(self, player_id: str) -> Optional[Player]:
        async with self._lock:
            return self._players.get(player_id)

    async def all_players(self) -> list[Player]:
        async with self._lock:
            return list(self._players.values())
    
    async def remove_player(self, player_id: str) -> bool:
        """Remove a player from the factory. Returns True if player was removed, False if not found."""
        async with self._lock:
            return self._players.pop(player_id, None) is not None
    
    async def get_player_count(self) -> int:
        """Get the total number of players."""
        async with self._lock:
            return len(self._players)
    
    async def update_player_stats(self, player_id: str, **stats) -> bool:
        """Update player statistics safely. Returns True if player was found and updated."""
        async with self._lock:
            player = self._players.get(player_id)
            if player and player.stats:
                for key, value in stats.items():
                    if hasattr(player.stats, key):
                        setattr(player.stats, key, value)
                return True
            return False
