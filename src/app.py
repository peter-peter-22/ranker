from fastapi import FastAPI
from src.routes.home import router as home_router
from src.routes.rank import router as rank_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Routers
app.include_router(home_router)
app.include_router(rank_router)
