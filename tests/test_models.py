import pytest
from datetime import datetime
from models import Game, Player, PlayerStats, Move, Status

MATRIX_SIZE = 3  # Assuming MATRIX_SIZE is defined globally in models.py


def test_player_stats_initialization():
    stats = PlayerStats()
    assert stats.gamesPlayed == 0
    assert stats.gamesWon == 0
    assert stats.gamesLost == 0
    assert stats.gamesDrawn == 0
    assert stats.totalMoves == 0
    assert stats.averageMovesPerWin == 0
    assert stats.efficiency == 0
    assert stats.winRate == 0


def test_player_initialization():
    player = Player(id="player_1", name="Player One", email="player1@example.com")
    assert player.id == "player_1"
    assert player.name == "Player One"
    assert player.email == "player1@example.com"
    assert isinstance(player.stats, PlayerStats)


def test_game_initialization():
    game = Game(id=1, name="Test Game")
    assert game.id == 1
    assert game.name == "Test Game"
    assert game.status == Status.PENDING
    assert game.board == [["","",""], ["","",""], ["","",""]]
    assert game.players == []
    assert game.currentPlayerId is None
    assert game.winnerId is None
    assert isinstance(game.createdAt, datetime)
    assert isinstance(game.updatedAt, datetime)
    assert game.moves == []


def test_make_move():
    player1 = Player(id="player_1", name="Player One", email="player1@example.com")
    player2 = Player(id="player_2", name="Player Two", email="player2@example.com")
    game = Game(id=1, players=[player1, player2], currentPlayerId=player1.id)

    # Make a valid move
    game.make_move(player_id="player_1", x=0, y=0)
    assert game.board[0][0] == "player_1"
    assert game.currentPlayerId == "player_2"

    # Attempt an invalid move (out of bounds)
    with pytest.raises(ValueError, match="Move \\(3, 3\\) is out of bounds"):
        game.make_move(player_id="player_2", x=3, y=3)

    # Attempt an invalid move (cell already occupied)
    with pytest.raises(ValueError, match="Cell \\(0, 0\\) is already occupied"):
        game.make_move(player_id="player_2", x=0, y=0)

    # Attempt a move out of turn
    with pytest.raises(ValueError, match="It's not your turn"):
        game.make_move(player_id="player_1", x=1, y=1)


def test_check_if_game_is_over():
    player1 = Player(id="player_1", name="Player One", email="player1@example.com")
    player2 = Player(id="player_2", name="Player Two", email="player2@example.com")
    game = Game(id=1, players=[player1, player2], currentPlayerId=player1.id)

    # Simulate a winning condition
    game.board = [
        ["player_1", "player_1", "player_1"],
        ["", "", ""],
        ["", "", ""],
    ]
    winner = game.check_if_game_is_over()
    assert winner == "player_1"
    assert game.status == Status.COMPLETED
    assert game.winnerId == "player_1"


def test_player_stats_update():
    player = Player(id="player_1", name="Player One", email="player1@example.com")
    player.stats.update_stats(won=True, draw=False, moves=5)
    assert player.stats.gamesPlayed == 1
    assert player.stats.gamesWon == 1
    assert player.stats.totalMoves == 5
    assert player.stats.averageMovesPerWin == 5
    assert player.stats.winRate == 1.0
    assert player.stats.efficiency == 5

    player.stats.update_stats(won=False, draw=True, moves=3)
    assert player.stats.gamesPlayed == 2
    assert player.stats.gamesDrawn == 1
    assert player.stats.totalMoves == 8
    assert player.stats.averageMovesPerWin == 5
    assert player.stats.winRate == 0.5
    assert player.stats.efficiency == 5


# Run the tests with pytest
if __name__ == "__main__":
    pytest.main()