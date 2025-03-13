# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from src.routes.home import router as home_router

app = FastAPI()

# routers
app.include_router(home_router)
