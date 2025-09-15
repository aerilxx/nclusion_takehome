# Tic-Tac-Toe Game API

A robust, thread-safe FastAPI-based tic-tac-toe game with player
statistics and leaderboards.

## 📋 Requirements

- Python 3.11
- FastAPI
- Pydantic (In-memory DB)
- Uvicorn (for running the server)

## ⚙️ Installation & Setup

### 1. Clone and Navigate
```bash
cd /path/to/folder
```

### 2. Install Dependencies
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## 🎮 API Usage Demo
```bash
/.demo_game.sh
```

#### Create a New Game
```bash
curl -s -X POST "http://localhost:8000/games" \
-H "Content-Type: application/json" \
-d '{"name": "My Awesome Game"}' | jq
```

**Response:**
```json
{
"game": {
"id": 1,
"name": "My Awesome Game"
},
"message": "Game 1 created successfully"
}
```

#### Get Game Status
```bash
curl -s -X GET "http://localhost:8000/games/1/status" | jq
```

**Response:**
```json
{
"status": {
"id": 1,
"status": "pending",
"board": [["", "", ""], ["", "", ""], ["", "", ""]],
"currentPlayerId": null,
"winnerId": null,
"players": [],
"moves": []
}
}
```

#### List All Games
```bash
# Get all games
curl -s -X GET "http://localhost:8000/games/" | jq

# Get games by status
curl -s -X GET "http://localhost:8000/games/?status=in_progress" | jq
curl -s -X GET "http://localhost:8000/games/?status=pending" | jq
curl -s -X GET "http://localhost:8000/games/?status=complete" | jq
```

#### Delete a Game
```bash
curl -s -X DELETE "http://localhost:8000/games/1" | jq
```

### Player Management & Game Play

#### Join a Game
```bash
# Player 1 joins
curl -s -X POST "http://localhost:8000/games/1/join" \
-H "Content-Type: application/json" \
-d '{
"playerId": "alice",
"name": "Alice Smith",
"email": "alice@example.com"
}' | jq

# Player 2 joins (game will start automatically)
curl -s -X POST "http://localhost:8000/games/1/join" \
-H "Content-Type: application/json" \
-d '{
"playerId": "bob",
"name": "Bob Johnson",
"email": "bob@example.com"
}' | jq
```

**Response:**
```json
{
"message": "alice Successfully joined game 1"
}
```
Raise error if playerID, email are not properly provided.


#### Make a Move
```bash
# Alice makes first move (top-left corner)
curl -s -X POST "http://localhost:8000/games/1/moves" \
-H "Content-Type: application/json" \
-d '{
"playerId": "alice",
"row": 0,
"col": 0
}' | jq

# Bob makes second move (center)
curl -s -X POST "http://localhost:8000/games/1/moves" \
-H "Content-Type: application/json" \
-d '{
"playerId": "bob",
"row": 1,
"col": 1
}' | jq
```

**Response:**
```json
{
"game": [["X", "", ""], ["", "", ""], ["", "", ""]],
"message": "Move made successfully",
"move": [0, 0],
"status": "in_progress"
}
```

### Leaderboards

#### Get Wins Leaderboard
```bash
# Default: page 1, limit 10
curl -s -X GET "http://localhost:8000/leaderboard/wins" | jq

# With pagination
curl -s -X GET "http://localhost:8000/leaderboard/wins?page=1&limit=5" | jq
```

**Response:**
```json
{
"leaderboard": [
{
"id": "alice",
"name": "Alice Smith",
"email": "alice@example.com",
"gamesPlayed": 5,
"gamesWon": 4,
"gamesLost": 1,
"gamesDrawn": 0,
"totalMoves": 20,
"averageMovesPerWin": 5.0,
"efficiency": 5.0,
"winRate": 0.8
}
],
"type": "wins"
}
```

#### Get Efficiency Leaderboard
```bash
curl -s -X GET "http://localhost:8000/leaderboard/efficiency?page=1&limit=10"
| jq
```


### Winning Conditions
- **Rows**: Three in a row horizontally
- **Columns**: Three in a row vertically
- **Diagonals**: Three in a row diagonally
- **Tie**: Board full with no winner

### Game Flow
1. Create game (status: `pending`)
2. Players join (2 players required)
3. Game starts automatically (status: `in_progress`)
4. Players alternate moves (X goes first)
5. Game ends when someone wins or board is full (status: `complete`)

## 🧪 Testing

### Run Unit Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_models.py -v
python -m pytest tests/test_factory_threading.py -v
```


## 📊 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/games` | Create a new game |
| `GET` | `/games/{id}` | Get game by ID |
| `GET` | `/games/{id}/status` | Get detailed game status |
| `GET` | `/games/` | List all games (with optional status filter) |
| `POST` | `/games/{id}/join` | Join a game |
| `POST` | `/games/{id}/moves` | Make a move |
| `DELETE` | `/games/{id}` | Delete a game |
| `GET` | `/leaderboard/wins` | Get leaderboard by wins |
| `GET` | `/leaderboard/efficiency` | Get leaderboard by efficiency |


## 🛠️ Design concerns

### Thread Safety
- **Async Locks**: All factory operations use `asyncio.Lock()` for thread safety
- **Game Locks**: Individual games have locks for move synchronization
- **Atomic Operations**: All state modifications are properly synchronized


## TODOs
- ✅ Add request logging middleware
- ✅ Implement Python models for Game and Player with in-memory store
- ✅ Complete games routes (status, join, moves, stats, delete, list)
- ✅ Add Python unit tests for models (Game/Player)
- ✅ Add player email validation
- ✅ Add validation for game creation and move inputs
- ✅ Complete players routes (update, delete, search)
- ✅ Validate Player model (name/email uniqueness, format)
- ✅ Standardize service error handling and messages
- ❌ Add basic request metrics with prom-client (Not formaliar with
promethues registry)


### Structure
- **Models**: Pydantic models for data validation (`models.py`)
- **Factories**: Thread-safe object creation and management (`factory.py`)
- **Routes**: RESTful API endpoints (`routes.py`)
- **Main**: FastAPI application setup (`main.py`)


## 🤝 AI Contributing

1. Using ChatGPT to gnerate the README and function level doumentation
2. Using Postman for API documentation
3. Using ChatGPT to format beautiful matrix in the shell script
4. Black for auto fix linting.
