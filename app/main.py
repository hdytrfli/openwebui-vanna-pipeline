from typing import Dict
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import questions, sql, data, training

load_dotenv()

origins = ["http://localhost", settings.origin_url]

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sql.router)
app.include_router(data.router)
app.include_router(training.router)
app.include_router(questions.router)
app.mount("/static", StaticFiles(directory=settings.static_folder), name="static")


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "status": "hello world",
        "version": settings.app_version,
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {
        "status": "healthy",
        "version": settings.app_version,
    }
