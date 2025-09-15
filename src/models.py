import logging
import asyncio
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Set board size to allow scalable 
MATRIX_SIZE = 3


class Status(str, Enum): 
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


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
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    stats: Optional[PlayerStats] = None

    def update_stats(self, won: bool, moves: int, draw: bool = False):
        """Once game completed, update the stats for both player"""
        self.stats.gamesPlayed += 1
        # assume moves are accumulated acorss different game 
        self.stats.totalMoves += moves
        if won:
            self.stats.gamesWon += 1
        elif draw:
            self.stats.gamesDrawn += 1
        else:
            self.stats.gamesLost += 1

        if self.stats.gamesWon > 0:
            self.stats.averageMovesPerWin = self.stats.totalMoves / self.stats.gamesWon
            self.stats.efficiency = self.stats.averageMovesPerWin
            self.stats.winRate = self.stats.gamesWon / self.stats.gamesPlayed
        else:
            self.stats.averageMovesPerWin = 0
            self.stats.efficiency = 0
            self.stats.winRate = 0


class Game(BaseModel):
    id: int
    name: Optional[str] = None
    status: Status = Status.PENDING
    # dict is mutable, need to make it thread-safe
    board: List[str] = Field(default_factory=lambda: [[""] * MATRIX_SIZE for _ in range(MATRIX_SIZE)])
    players: List[Player] = Field(default_factory=list)
    currentPlayerId: Optional[str] = None
    winnerId: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    moves: List[Move] = Field(default_factory=list)
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock, repr=False)

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    def check_if_game_is_over(self) -> Optional[str]:
        n = MATRIX_SIZE
        b = self.board 
        for i in range(n):
            if b[i][0] != "" and all(b[i][j] == b[i][0] for j in range(n)):
                return f"Row {i} forms a line! Game is Over!"
        for j in range(n):
            if b[0][j] != "" and all(b[i][j] == b[0][j] for i in range(n)):
                return f"Column {j} forms a line! Game is Over!"
        if b[0][0] != "" and all(b[i][i] == b[0][0] for i in range(n)):
            return "Main diagonal forms a line! Game is Over!"
        if b[0][n-1] != "" and all(b[i][n-1-i] == b[0][n-1] for i in range(n)):
            return "Anti-diagonal forms a line! Game is Over!"
        if all(cell != "" for row in b for cell in row):
            return "TIE"
        return None
    
    async def make_move(self, player_id: str, row: int, col: int) -> bool:
        """Migrate make_move function from route to dataclass to readability 
        and ease of maintain. Also improve threading-safe easier.
        """
        async with self.lock:
            print(f"Before move: currentPlayerId={self.currentPlayerId}")
            if self.status != Status.IN_PROGRESS:
                logger.error(f"Game is not active!")
                return False
            
            if self.currentPlayerId != player_id:
                logger.error(f"Not your turn!")
                return False
            
            if row < 0 or row >= MATRIX_SIZE or col < 0 or col >= MATRIX_SIZE:
                logger.error(f"Move coordinates must be between 0 and {MATRIX_SIZE}!")
                return False
            
            if self.board[row][col] != "":
                logger.error("Cell is already occupied!")
                return False

            player_index = next((i for i, player in enumerate(self.players) if player.id == player_id), -1)
            if player_index == -1:
                raise ValueError(f"Player ID '{player_id}' not found in the game.")
            symbol = "X" if player_index == 0 else "O"
            self.board[row][col] = symbol
            self.updatedAt = datetime.now()
            self.moves.append(
                Move(
                    id=f"m-{len(self.moves)+1}", 
                    gameId=str(self.id), 
                    playerId=player_id,
                    row=row, 
                    col=col, 
                    timestamp=datetime.now()
                )
            )

            over = self.check_if_game_is_over()
            if over:
                self.status = Status.COMPLETE
                self.winnerId = player_id if over != "TIE" else None
                await self.end_game()
            else:
                self.currentPlayerId = self.players[1].id if self.currentPlayerId == self.players[0].id else self.players[0].id
            print(f"After move: currentPlayerId={self.currentPlayerId}")
            return True 
        
    async def end_game(self):
        """Update player stats after game is over
        """
        for player in self.players:
            moves_in_game = sum(1 for move in self.moves if move.playerId == player.id)
            won = player.id == self.winnerId
            draw = won is None
            player.update_stats(won=won, moves=moves_in_game, draw=draw)
        logger.info(f"Game {self.id} ended. Winner: {self.winnerId or 'Draw'}")
