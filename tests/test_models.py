import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Status, Move, PlayerStats, Player, Game, MATRIX_SIZE


class TestMove:
    """Test cases for Move model"""
    
    def test_move_creation_valid(self):
        """Test creating a valid Move instance"""
        move_data = {
            "id": "move_1",
            "gameId": "game_1",
            "playerId": "player_1",
            "row": 1,
            "col": 2,
            "timestamp": datetime.now()
        }
        move = Move(**move_data)
        
        assert move.id == "move_1"
        assert move.gameId == "game_1"
        assert move.playerId == "player_1"
        assert move.row == 1
        assert move.col == 2
        assert isinstance(move.timestamp, datetime)
    
    def test_move_validation_missing_fields(self):
        """Test Move validation with missing required fields"""
        with pytest.raises(ValidationError):
            Move(id="move_1", gameId="game_1")  # Missing required fields
    
    def test_move_validation_invalid_types(self):
        """Test Move validation with invalid field types"""
        with pytest.raises(ValidationError):
            Move(
                id="move_1",
                gameId="game_1", 
                playerId="player_1",
                row="invalid",  # Should be int
                col=2,
                timestamp=datetime.now()
            )


class TestPlayer:
    """Test cases for Player model"""
    
    def test_player_creation_minimal(self):
        """Test creating a Player with minimal data"""
        player = Player(id="player_1")
        
        assert player.id == "player_1"
        assert player.name is None
        assert player.email is None
        assert player.stats is None
    
    def test_player_creation_full(self):
        """Test creating a Player with full data"""
        stats = PlayerStats(gamesPlayed=5, gamesWon=3)
        player = Player(
            id="player_1",
            name="John Doe",
            email="john@example.com",
            stats=stats
        )
        
        assert player.id == "player_1"
        assert player.name == "John Doe"
        assert player.email == "john@example.com"
        assert player.stats == stats
    
    def test_player_invalid_email(self):
        """Test Player validation with invalid email"""
        with pytest.raises(ValidationError):
            Player(id="player_1", email="invalid_com")
    
    def test_update_stats_multiple_games(self):
        """Test update_stats method across multiple games"""
        player = Player(id="player_1", stats=PlayerStats())
        
        # First game - win
        player.update_stats(won=True, moves=4)
        # Second game - loss  
        player.update_stats(won=False, moves=6)
        # Third game - win
        player.update_stats(won=True, moves=8)
        
        assert player.stats.gamesPlayed == 3
        assert player.stats.gamesWon == 2
        assert player.stats.gamesLost == 1
        assert player.stats.gamesDrawn == 0
        assert player.stats.totalMoves == 18
        assert player.stats.averageMovesPerWin == 9.0  # 18 total moves / 2 wins
        assert player.stats.efficiency == 9.0
        assert player.stats.winRate == 2/3  # 2 wins / 3 games


class TestGame:
    """Test cases for Game model"""
    
    def test_game_creation_minimal(self):
        """Test creating a Game with minimal data"""
        game = Game(id=1)
        
        assert game.id == 1
        assert game.name is None
        assert game.status == Status.PENDING
        assert len(game.board) == MATRIX_SIZE
        assert len(game.board[0]) == MATRIX_SIZE
        assert all(cell == "" for row in game.board for cell in row)
        assert game.players == []
        assert game.currentPlayerId is None
        assert game.winnerId is None
        assert isinstance(game.createdAt, datetime)
        assert isinstance(game.updatedAt, datetime)
        assert game.moves == []
        assert isinstance(game.lock, asyncio.Lock)
    
    def test_game_creation_full(self):
        """Test creating a Game with full data"""
        players = [Player(id="p1"), Player(id="p2")]
        game = Game(
            id=1,
            name="Test Game",
            status=Status.IN_PROGRESS,
            players=players,
            currentPlayerId="p1"
        )
        
        assert game.id == 1
        assert game.name == "Test Game"
        assert game.status == Status.IN_PROGRESS
        assert game.players == players
        assert game.currentPlayerId == "p1"
    
    def test_check_if_game_is_over_empty_board(self):
        """Test check_if_game_is_over with empty board"""
        game = Game(id=1)
        result = game.check_if_game_is_over()
        assert result is None
    
    def test_check_if_game_is_over_row_win(self):
        """Test check_if_game_is_over with row win"""
        game = Game(id=1)
        # Fill first row with X's
        for col in range(MATRIX_SIZE):
            game.board[0][col] = "X"
        
        result = game.check_if_game_is_over()
        assert result == "Row 0 forms a line! Game is Over!"
    
    def test_check_if_game_is_over_column_win(self):
        """Test check_if_game_is_over with column win"""
        game = Game(id=1)
        # Fill first column with O's
        for row in range(MATRIX_SIZE):
            game.board[row][0] = "O"
        
        result = game.check_if_game_is_over()
        assert result == "Column 0 forms a line! Game is Over!"
    
    def test_check_if_game_is_over_tie(self):
        """Test check_if_game_is_over with board full (tie)"""
        game = Game(id=1)
        # Fill board with no winning pattern but full board
        game.board = [
            ["X", "O", "X"],
            ["O", "X", "O"], 
            ["O", "X", "O"]
        ]
        
        result = game.check_if_game_is_over()
        assert result == "TIE"
    
    @pytest.mark.asyncio
    async def test_make_move_game_not_active(self):
        """Test make_move when game is not in progress"""
        game = Game(id=1, status=Status.PENDING)
        result = await game.make_move("player1", 0, 0)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_make_move_wrong_player_turn(self):
        """Test make_move when it's not the player's turn"""
        players = [Player(id="p1"), Player(id="p2")]
        game = Game(id=1, status=Status.IN_PROGRESS, players=players, currentPlayerId="p1")
        
        result = await game.make_move("p2", 0, 0)  # Wrong player
        assert result is False
    
    @pytest.mark.asyncio
    async def test_make_move_invalid_coordinates(self):
        """Test make_move with invalid coordinates"""
        players = [Player(id="p1"), Player(id="p2")]
        game = Game(id=1, status=Status.IN_PROGRESS, players=players, currentPlayerId="p1")
        
        # Test negative coordinates
        result = await game.make_move("p1", -1, 0)
        assert result is False
        
        # Test coordinates too large
        result = await game.make_move("p1", MATRIX_SIZE, 0)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_make_move_cell_occupied(self):
        """Test make_move when cell is already occupied"""
        players = [Player(id="p1"), Player(id="p2")]
        game = Game(id=1, status=Status.IN_PROGRESS, players=players, currentPlayerId="p1")
        game.board[0][0] = "X"  # Occupy cell
        
        result = await game.make_move("p1", 0, 0)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_make_move_player_not_in_game(self):
        """Test make_move with player not in the game"""
        players = [Player(id="p1"), Player(id="p2")]
        game = Game(id=1, status=Status.IN_PROGRESS, players=players, currentPlayerId="p3")  # Set current player to p3
        
        with pytest.raises(ValueError, match="Player ID 'p3' not found in the game"):
            await game.make_move("p3", 0, 0)
    
    @pytest.mark.asyncio
    async def test_make_move_successful(self):
        """Test successful make_move"""
        players = [Player(id="p1"), Player(id="p2")]
        game = Game(id=1, status=Status.IN_PROGRESS, players=players, currentPlayerId="p1")
        
        result = await game.make_move("p1", 1, 1)
        
        assert result is True
        assert game.board[1][1] == "X"  # First player gets X
        assert len(game.moves) == 1
        assert game.moves[0].playerId == "p1"
        assert game.moves[0].row == 1
        assert game.moves[0].col == 1
        assert game.currentPlayerId == "p2"  # Turn switches to player 2 id
    
    @pytest.mark.asyncio
    async def test_make_move_winning_move(self):
        """Test make_move that results in a win"""
        players = [Player(id="p1", stats=PlayerStats()), Player(id="p2", stats=PlayerStats())]
        game = Game(id=1, status=Status.IN_PROGRESS, players=players, currentPlayerId="p1")
        
        # Set up a winning condition (2 X's in top row)
        game.board[0][0] = "X"
        game.board[0][1] = "X"
        game.moves = [
            Move(id="m-1", gameId="1", playerId="p1", row=0, col=0, timestamp=datetime.now()),
            Move(id="m-2", gameId="1", playerId="p1", row=0, col=1, timestamp=datetime.now())
        ]
        
        result = await game.make_move("p1", 0, 2)  # Winning move
        
        assert result is True
        assert game.board[0][2] == "X"
        assert game.winnerId == "p1"
        # Check whether end_game was called
        assert players[0].stats.gamesPlayed == 1
        assert players[0].stats.gamesWon == 1
    
    @pytest.mark.asyncio
    async def test_end_game(self):
        """Test end_game method"""
        players = [
            Player(id="p1", stats=PlayerStats()),
            Player(id="p2", stats=PlayerStats())
        ]
        game = Game(id=1, players=players, winnerId="p1")
        # Moves are stored as Move objects
        game.moves = [
            Move(id="m-1", gameId="1", playerId="p1", row=0, col=0, timestamp=datetime.now()),
            Move(id="m-2", gameId="1", playerId="p2", row=1, col=1, timestamp=datetime.now()),
            Move(id="m-3", gameId="1", playerId="p1", row=0, col=1, timestamp=datetime.now())
        ]
        
        await game.end_game()
        
        # Player 1 should have won
        assert players[0].stats.gamesPlayed == 1
        assert players[0].stats.gamesWon == 1
        assert players[0].stats.totalMoves == 2  # 2 moves in the game
        
        # Player 2 should have lost
        assert players[1].stats.gamesPlayed == 1
        assert players[1].stats.gamesLost == 1
        assert players[1].stats.totalMoves == 1  # 1 move in the game


if __name__ == "__main__":
    pytest.main([__file__])
