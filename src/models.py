from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Move(BaseModel):
    id: str
    gameId: str
    playerId: str
    row: int
    col: int
    timestamp: datetime


class PlayerStats(BaseModel):
    gamesPlayed: int = 0
    gamesWon: int = 0
    gamesLost: int = 0
    gamesDrawn: int = 0
    totalMoves: int = 0
    averageMovesPerWin: float = 0
    winRate: float = 0
    efficiency: float = 0


class Player(BaseModel):
    id: str
    name: str
    email: EmailStr
    stats: PlayerStats
    createdAt: datetime
    updatedAt: datetime


class Game(BaseModel):
    id: str
    name: Optional[str]
    status: str
    board: List[List[Optional[str]]]
    players: List[Player]
    currentPlayerId: Optional[str]
    winnerId: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    moves: List[Move]



// TODO: Implement Python models for Game and Player with in-memory store [ttt.todo.py.models.complete]
// TODO: Add player email validation [ttt.todo.validation.player-email]