from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

games = APIRouter(prefix="/games")

class CreateGameRequest(BaseModel):
    name: Optional[str] = None

class JoinGameRequest(BaseModel):
    playerId: str

class MakeMoveRequest(BaseModel):
    playerId: str
    row: int
    col: int

# Minimal in-memory store
_GAMES: dict = {}

@games.post("/")
def create_game(body: CreateGameRequest):
    # TODO: validate name length
    game_id = f"game-{len(_GAMES)+1}"
    _GAMES[game_id] = {
        "id": game_id,
        "name": body.name or game_id,
        "status": "waiting",
        "board": [[None, None, None] for _ in range(3)],
        "players": [],
        "currentPlayerId": None,
        "winnerId": None,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "moves": [],
    }
    return {"game": _GAMES[game_id], "message": "Game created successfully"}

@games.get("/{id}")
def get_game(id: str):
    game = _GAMES.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"game": game}

@games.get("/{id}/status")
def get_status(id: str):
    game = _GAMES.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"status": {
        "id": game["id"],
        "status": game["status"],
        "board": game["board"],
        "currentPlayerId": game["currentPlayerId"],
        "winnerId": game["winnerId"],
        "players": game["players"],
        "moves": game["moves"],
    }}

@games.post("/{id}/join")
def join_game(id: str, body: JoinGameRequest):
    game = _GAMES.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game["status"] != "waiting":
        raise HTTPException(status_code=400, detail="Game is not accepting new players")
    if len(game["players"]) >= 2:
        raise HTTPException(status_code=400, detail="Game is full")
    player = {"id": body.playerId, "name": body.playerId}
    if any(p["id"] == body.playerId for p in game["players"]):
        raise HTTPException(status_code=400, detail="Player already in the game")
    game["players"].append(player)
    if len(game["players"]) == 2:
        game["status"] = "active"
        game["currentPlayerId"] = game["players"][0]["id"]
    game["updatedAt"] = datetime.utcnow().isoformat()
    return {"game": game, "message": "Successfully joined game"}

@games.post("/{id}/moves")
def make_move(id: str, body: MakeMoveRequest):
    game = _GAMES.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game["status"] != "active":
        raise HTTPException(status_code=400, detail="Game is not active")
    if game["currentPlayerId"] != body.playerId:
        raise HTTPException(status_code=400, detail="Not your turn")
    r, c = body.row, body.col
    if r < 0 or r > 2 or c < 0 or c > 2:
        raise HTTPException(status_code=400, detail="Move coordinates must be between 0 and 2")
    if game["board"][r][c] is not None:
        raise HTTPException(status_code=400, detail="Cell is already occupied")
    game["board"][r][c] = body.playerId
    game["moves"].append({"id": f"m-{len(game['moves'])+1}", "gameId": id, "playerId": body.playerId, "row": r, "col": c, "timestamp": datetime.utcnow().isoformat()})
    // TODO: check win/draw and flip current player
    game["updatedAt"] = datetime.utcnow().isoformat()
    return {"game": game, "move": game["moves"][-1], "message": "Move made successfully"}

@games.get("/{id}/moves")
def get_valid_moves(id: str):
    game = _GAMES.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game["status"] != "active":
        raise HTTPException(status_code=400, detail="Game is not active")
    valid = [{"row": r, "col": c} for r in range(3) for c in range(3) if game["board"][r][c] is None]
    return {"validMoves": valid, "count": len(valid)}

@games.get("/")
def list_games(status: Optional[str] = None):
    games = list(_GAMES.values())
    if status:
        games = [g for g in games if g["status"] == status]
    return {"games": games, "count": len(games)}

@games.delete("/{id}")
def delete_game(id: str):
    game = _GAMES.get(id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game["status"] == "active":
        raise HTTPException(status_code=400, detail="Cannot delete an active game")
    _GAMES.pop(id, None)
    return {"message": "Game deleted successfully"}

leaderboard = APIRouter(prefix="/leaderboard")

@leaderboard.get("/")
def leaderboard_wins(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    # TODO: Implement leaderboard by wins
    return {"leaderboard": [], "type": "wins"}

@leaderboard.get("/efficiency")
def leaderboard_efficiency(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    # TODO: Implement leaderboard by efficiency
    return {"leaderboard": [], "type": "efficiency"}



// TODO: Add validation for game creation and move inputs [ttt.todo.validation.game-inputs]