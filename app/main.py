from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.db import initialize_database

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await initialize_database()


@app.get("/")
async def redirect_to_docs():
    return RedirectResponse("/docs")
