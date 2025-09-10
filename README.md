# Backend SWE Take-Home Assignment - Python

## Overview

This is a **3-4 hour take-home assignment**. You will build a small, network-accessible backend web service that manages a turn-based, grid-driven game from pre-defined rules. Your assignment is tailored: a randomized (but reproducible) set of TODOs, features, and bugs has been embedded inline.

You should focus on:
- Clear, maintainable API handlers and service logic
- Robust input validation and error handling
- Simple, reliable tests (unit and integration)
- Helpful logs/metrics stubs where applicable

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip or uv

### Installation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Application

```bash
uvicorn src.main:app --reload --port 8000
```

The application will start on port 8000.

### Running Tests

```bash
pytest
```

### Running the Simulation

> Optional: You may create a simple simulation script or test that spins up your server, plays multiple sessions concurrently, and prints a small leaderboard summary.

## Project Structure

```
src/
├── main.py
├── models.py
├── routes.py
└── services.py
```

## What You Need to Implement

### Selected Tasks

#### TODOs
- Add request logging middleware
- Implement Python models for Game and Player with in-memory store
- Complete games routes (status, join, moves, stats, delete, list)
- Add Python unit tests for models (Game/Player)
- Add player email validation
- Add validation for game creation and move inputs
- Complete players routes (update, delete, search)
- Validate Player model (name/email uniqueness, format)
- Standardize service error handling and messages

#### Feature Requests
- Add basic request metrics with prom-client

#### Bugs To Fix
- Move bounds check off-by-one allows row&#x3D;3 or col&#x3D;3 (symptom: )

### Core Requirements (high-level)

1. Turn-based rules on a finite grid with obvious invalid-move conditions
2. Multiple sessions can run concurrently; two players start a session
3. End a session on win or draw; expose session status
4. Leaderboard endpoint returning top users by wins or "efficiency" (lower moves per win is better)
5. A small simulation or test path that exercises the API

Additionally, look for inline TODOs in language-appropriate files. Examples:
- Python: `src/routes.py`, `src/models.py`, `src/main.py`

> Focus on correctness, quality, and clarity. If you finish early, feel free to polish or extend.

## Notes

- Inline TODOs are your primary guide. GitHub Issues are intentionally disabled.
- Keep commits small and frequent with clear messages.
- You may add libraries if they help you implement tasks cleanly.

## Quick API Examples

Assuming your server is running on http://localhost:8000

Create a game
```bash
curl -s -X POST http://localhost:8000/games -H 'Content-Type: application/json' -d '{"name":"Sample"}' | jq .
```

Join the game
```bash
GAME_ID=<paste-from-create>
curl -s -X POST http://localhost:8000/games/$GAME_ID/join -H 'Content-Type: application/json' -d '{"playerId":"player-1"}' | jq .
curl -s -X POST http://localhost:8000/games/$GAME_ID/join -H 'Content-Type: application/json' -d '{"playerId":"player-2"}' | jq .
```

Make a move and get status
```bash
curl -s -X POST http://localhost:8000/games/$GAME_ID/moves -H 'Content-Type: application/json' -d '{"playerId":"player-1","row":0,"col":0}' | jq .
curl -s http://localhost:8000/games/$GAME_ID/status | jq .
```

Leaderboard (optional)
```bash
curl -s http://localhost:8000/leaderboard | jq .
```

## Submission

1. Ensure tests pass
2. Run the simulation script
3. Update this README with any setup notes
4. Submit your repository URL

Good luck! 🚀
