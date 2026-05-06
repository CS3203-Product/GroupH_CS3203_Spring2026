from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.endpoints import blocker, login as login_endpoints
from src.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db.init()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_endpoints.router, tags=["login"])
app.include_router(blocker.router, tags=["blocker"])
