from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.db import initialize_database
from app.routers.auth import auth_router
from app.routers.event import event_router
from app.routers.group import group_router
from app.routers.user import user_router

VERSION_PREFIX = "/api/v1"

app = FastAPI(
    title="WetinDeySup Backend",
    description="A python equivalent of the events app by TEAM-FORTRESS",
)
app.include_router(auth_router, prefix=VERSION_PREFIX)
app.include_router(user_router, prefix=VERSION_PREFIX)
app.include_router(group_router, prefix=VERSION_PREFIX)
app.include_router(event_router, prefix=VERSION_PREFIX)


@app.on_event("startup")
async def on_startup():
    await initialize_database()


# @app.on_event("shutdown")
# async def on_shutdown():
#     await teardown_database()


@app.get("/")
async def redirect_to_docs():
    return RedirectResponse("/docs")
