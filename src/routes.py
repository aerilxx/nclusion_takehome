import logging

from fastapi import  APIRouter, Query, HTTPException, Response
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from .factory import GameFactory, PlayerFactory
from .models import Status


logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

games = APIRouter(prefix="/games")
leaderboard = APIRouter(prefix="/leaderboard")

class CreateGameRequest(BaseModel):
    name: str

class JoinGameRequest(BaseModel):
    playerId: str
    name: Optional[str] = None
    email: EmailStr

class MakeMoveRequest(BaseModel):
    playerId: str
    row: int
    col: int

game_factory = GameFactory()
player_factory = PlayerFactory()

@games.post("")
async def create_game(body: CreateGameRequest):
    game_name = body.name or f"Game {game_factory._next_id + 1}"
    logging.info(f"Game {game_name} is On.")
    game = await game_factory.create_game(game_name)
    return {
        "game": {
            "id": game.id,
            "name": game.name
        },
        "message": f"Game {game.id} created successfully"
    }


@games.get("/{id}")
async def get_game(id: int):
    game = await game_factory.get_game(id)
    if not game:
        raise HTTPException(status_code=404, detail=f"Game {id} not found")
    return Response(status_code=200)


@games.get("/{id}/status")
async def get_status(id: str):
    game = await game_factory.get_game(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"status": {
        "id": game.id,
        "status": game.status,
        "board": game.board,
        "currentPlayerId": game.currentPlayerId,
        "winnerId": game.winnerId,
        "players": game.players,
        "moves": game.moves,
    }}


@games.post("/{id}/join")
async def join_game(id: int, body: JoinGameRequest):
    game = await game_factory.get_game(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if len(game.players) >= 2:
        raise HTTPException(status_code=400, detail="Game is full")
    
    player = await player_factory.get_or_create_player(player_id=body.playerId, name=body.name, email=body.email)
    if any(p.id == body.playerId for p in game.players):
        raise HTTPException(status_code=400, detail="Player already in the game")
    
    if all(p.id != player.id for p in game.players):
        game.players.append(player)
    if len(game.players) == 2:
        game.status = Status.IN_PROGRESS
        game.currentPlayerId = game.players[0].id
        logging.info("Game is good to start.")
    return {"message": f"{player.id} Successfully joined game {id}"}


@games.post("/{id}/moves")
async def make_move(id: int, body: MakeMoveRequest):
    game = await game_factory.get_game(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    move = await game.make_move(body.playerId, body.row, body.col)
    if not move:
        raise HTTPException(400, "Invalid move")
    return {
        "game": game.board,
        "message": "Move made successfully",
        "move": [body.row, body.col],
        "status": game.status
    }


@games.get("/")
async def list_games(status: Optional[str] = None):
    """List all games or games under different status
    """
    games = list(game_factory._games.values())
    if status:
        games = [g for g in games if g.status == status]
    else:
        games_list = games
     # Convert Pydantic models to dicts for JSON serialization
    games_list = [g.id for g in games]
    return {f"{status} games": games_list, "count": len(games_list)}


@games.delete("/{id}")
def delete_game(id: str):
    game = game_factory.get_game(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status == Status.in_progress:
        raise HTTPException(status_code=400, detail="Cannot delete an active game")
    game_factory.pop(id, None)
    return Response(status_code=200)


@leaderboard.get("/wins")
async def leaderboard_wins(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Returns leaderboard sorted by total wins.
    """
    all_players = await player_factory.all_players()
    sorted_players = sorted(all_players, key=lambda p: p.stats.gamesWon, reverse=True)

    start = (page - 1) * limit
    end = start + limit
    paged_players = sorted_players[start:end]

    response = [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "gamesPlayed": p.stats.gamesPlayed,
            "gamesWon": p.stats.gamesWon,
            "gamesLost": p.stats.gamesLost,
            "gamesDrawn": p.stats.gamesDrawn,
            "totalMoves": p.stats.totalMoves,
            "averageMovesPerWin": p.stats.averageMovesPerWin,
            "efficiency": p.stats.efficiency,
            "winRate": p.stats.winRate,
        }
        for p in paged_players
    ]

    return {
        "leaderboard": response,
        "type": "wins"
    }

@leaderboard.get("/efficiency")
async def leaderboard_efficiency(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Returns leaderboard sorted by player efficiency.
    """
    all_players = await player_factory.all_players()
    sorted_players = sorted(all_players, key=lambda p: p.stats.efficiency, reverse=True)

    start = (page - 1) * limit
    end = start + limit
    paged_players = sorted_players[start:end]

    response = [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "gamesPlayed": p.stats.gamesPlayed,
            "gamesWon": p.stats.gamesWon,
            "gamesLost": p.stats.gamesLost,
            "gamesDrawn": p.stats.gamesDrawn,
            "totalMoves": p.stats.totalMoves,
            "averageMovesPerWin": p.stats.averageMovesPerWin,
            "efficiency": p.stats.efficiency,
            "winRate": p.stats.winRate,
        }
        for p in paged_players
    ]

    return {
        "leaderboard": response,
        "type": "efficiency"
    }