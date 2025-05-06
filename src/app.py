from fastapi import FastAPI
from src.routes.home import router as home_router
from src.routes.rank import router as rank_router
from src.routes.train import router as train_router
from pathlib import Path

# Define root path
root_path=current_file_path = Path(__file__).parent
# Routers
app = FastAPI()
app.include_router(home_router)
app.include_router(rank_router)
app.include_router(train_router)