from fastapi import FastAPI
from .routes import games, leaderboard

app = FastAPI()
app.include_router(games)
app.include_router(leaderboard)
