import asyncio
from typing import Dict, Optional
from .models import Game, Player, Status


class GameFactory:
    def __init__(self):
        self._games: Dict[int, Game] = {}
        self._next_id = 1
        self._lock = asyncio.Lock()
    
    # Can be elegant if not using in-memory pandatic...
    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    async def create_game(self, name: str) -> Game:
        async with self._lock:
            game_id = self._next_id
            self._next_id += 1
            print(f"create game {name} for {game_id} time")
            game = Game(id=game_id, name=name, status=Status.PENDING)
            self._games[game_id] = game
        return game

    async def get_game(self, game_id: int) -> Optional[Game]:
        async with self._lock:
            return self._games.get(game_id)



class PlayerFactory:
    def __init__(self):
        self._players: Dict[str, Player] = {}
        self._lock = asyncio.Lock()

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
    
    async def get_or_create_player(self, player_id: str, email: Optional[str], name: Optional[str]) -> Player:
        async with self._lock:
            if player_id in self._players:
                return self._players[player_id]
            player = Player(id=player_id, email=email, name=name)
            self._players[player_id] = player
            return player

    async def get_player(self, player_id: str) -> Optional[Player]:
        return self._players.get(player_id)

    async def all_players(self) -> list[Player]:
        return list(self._players.values())
