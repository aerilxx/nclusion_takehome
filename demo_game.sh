#!/bin/bash

# Complete Game Demo. This script demonstrates how API works using shell script to verify
# functionality of the routes.

BASE_URL="http://localhost:8000"

# Function to format board as 3x3 matrix and human readable board
format_board() {
    jq -r '(if .game then .game elif .status.board then .status.board else .board end) | map(map(if . == "" then "·" else . end) | join(" | ")) | join("\n---------\n")'
}

format_board_fancy() {
    jq -r '
    if .detail then 
        "❌ Error: " + .detail
    else
        (if .game then .game elif .status.board then .status.board else .board end) | 
        if . == null then 
            "❌ Error: No board data found"
        else
            map(map(if . == "" then " " else . end)) |
            "┌───┬───┬───┐",
            "│ \(.[0][0]) │ \(.[0][1]) │ \(.[0][2]) │",
            "├───┼───┼───┤", 
            "│ \(.[1][0]) │ \(.[1][1]) │ \(.[1][2]) │",
            "├───┼───┼───┤",
            "│ \(.[2][0]) │ \(.[2][1]) │ \(.[2][2]) │", 
            "└───┴───┴───┘"
        end
    end
    '
}

echo "🎮 Tic-Tac-Toe Game API Demo"
echo "============================"

# Check if server is running
echo "Checking if server is running..."
if ! curl -s "$BASE_URL/docs" > /dev/null; then
    echo "❌ Server not running! Please start the server first:"
    echo "   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi
echo "✅ Server is running!"

# 1. Create a new game
echo -e "\n🎯 Step 1: Creating Game"
echo "========================"
GAME_RESPONSE=$(curl -s -X POST "$BASE_URL/games" \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo Game"}')
echo $GAME_RESPONSE | jq

GAME_ID=$(echo $GAME_RESPONSE | jq -r '.game.id')
echo "🎲 Game ID: $GAME_ID"

# 2. Player 1 joins
echo -e "\n👤 Step 2: Player 1 Joining"
echo "==========================="
curl -s -X POST "$BASE_URL/games/$GAME_ID/join" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "alice",
    "name": "Alice",
    "email": "alice@example.com"
  }' | jq

# 3. Player 2 joins (game starts automatically)
echo -e "\n👤 Step 3: Player 2 Joining (Game Starts!)"
echo "=========================================="
curl -s -X POST "$BASE_URL/games/$GAME_ID/join" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "bob",
    "name": "Bob",
    "email": "bob@example.com"
  }' | jq

# 4. Player 3 joins (Raise Error)
echo -e "\n👤 Step 4: Player 2 Joining (Game Starts!)"
echo "=========================================="
curl -s -X POST "$BASE_URL/games/$GAME_ID/join" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "player_3",
    "name": "aeril",
    "email": "aeril@example.com"
  }' | jq

# 5. Check initial game status
echo -e "\n📊 Step 5: Initial Game Status"
echo "=============================="
curl -s -X GET "$BASE_URL/games/$GAME_ID/status" | jq '.status | {id, status, currentPlayerId, board}'


# 6. Create a fresh game for moves demo
echo -e "\n🎯 Step 6: Creating Fresh Game for Moves Demo"
echo "=============================================="
FRESH_GAME_RESPONSE=$(curl -s -X POST "$BASE_URL/games" \
  -H "Content-Type: application/json" \
  -d '{"name": "Fresh Game for Moves"}')
echo $FRESH_GAME_RESPONSE | jq

FRESH_GAME_ID=$(echo $FRESH_GAME_RESPONSE | jq -r '.game.id')
echo "🎲 Fresh Game ID: $FRESH_GAME_ID"

# Add players to fresh game
echo -e "\n👤 Adding Alice to fresh game"
curl -s -X POST "$BASE_URL/games/$FRESH_GAME_ID/join" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "alice_fresh",
    "name": "Alice Fresh",
    "email": "alice.fresh@example.com"
  }' | jq

echo -e "\n👤 Adding Bob to fresh game"
curl -s -X POST "$BASE_URL/games/$FRESH_GAME_ID/join" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "bob_fresh",
    "name": "Bob Fresh",
    "email": "bob.fresh@example.com"
  }' | jq

# 8. Play the game - Alice wins with top row
echo -e "\n🎮 Step 8: Playing the Fresh Game"
echo "================================="

echo "Move 1: Alice Fresh (X) plays top-left (0,0)"
curl -s -X POST "$BASE_URL/games/$FRESH_GAME_ID/moves" \
  -H "Content-Type: application/json" \
  -d '{"playerId": "alice_fresh", "row": 0, "col": 0}' | format_board_fancygame in  

echo -e "\nMove 2: Bob Fresh (O) plays center (1,1)"
curl -s -X POST "$BASE_URL/games/$FRESH_GAME_ID/moves" \
  -H "Content-Type: application/json" \
  -d '{"playerId": "bob_fresh", "row": 1, "col": 1}' | format_board_fancy

echo -e "\nMove 3: Alice Fresh (X) plays top-middle (0,1)"
curl -s -X POST "$BASE_URL/games/$FRESH_GAME_ID/moves" \
  -H "Content-Type: application/json" \
  -d '{"playerId": "alice_fresh", "row": 0, "col": 1}' | format_board_fancy

echo -e "\nMove 4: Bob Fresh (O) plays bottom-right (2,2)"
curl -s -X POST "$BASE_URL/games/$FRESH_GAME_ID/moves" \
  -H "Content-Type: application/json" \
  -d '{"playerId": "bob_fresh", "row": 2, "col": 2}' | format_board_fancy

echo -e "\n🏆 Move 5: Alice Fresh (X) plays top-right (0,2) - WINNING MOVE!"
WINNING_RESPONSE=$(curl -s -X POST "$BASE_URL/games/$FRESH_GAME_ID/moves" \
  -H "Content-Type: application/json" \
  -d '{"playerId": "alice_fresh", "row": 0, "col": 2}')
echo $WINNING_RESPONSE | format_board_fancy

# 7. Check final game status
echo -e "\n🎉 Step 7: Final Game Status"
echo "============================"
curl -s -X GET "$BASE_URL/games/$GAME_ID/status" | jq '.status | {id, status, winnerId, board: .board}'

# 8. Check updated leaderboard
echo -e "\n🏆 Step 8: Updated Leaderboard"
echo "============================="
curl -s -X GET "$BASE_URL/leaderboard/wins" | jq

# 9. List all games
echo -e "\n📋 Step 9: All Games"
echo "==================="
curl -s -X GET "$BASE_URL/games/" | jq

echo -e "\n✨ Demo Complete!"
echo "================="
echo "🎊 Alice won the game with a top row!"
echo "📊 Check the leaderboard to see updated statistics"
echo "🔄 Run this script again to play another game"
echo ""
echo "For more examples, see: README.md"
