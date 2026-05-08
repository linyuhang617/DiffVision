from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import upload

load_dotenv()

app = FastAPI(title="DiffVision", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

Path("temp").mkdir(exist_ok=True)
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
app.mount("/", StaticFiles(directory="static", html=True), name="static")
