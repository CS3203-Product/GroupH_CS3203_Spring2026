from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from nicegui import app, ui

from src.backend.endpoints import blocker, items, login, users
from src.core.config import settings
from src.db import init_db
from src.frontend.theme import apply_productive_theme

_ROOT = Path(__file__).resolve().parent
app.add_static_files("/assets/sound", str(_ROOT / "assets" / "sound"))
apply_productive_theme()

# ruff: noqa: F401 — register NiceGUI pages
from src.frontend.pages import (
    ambient,
    collaboration,
    create_user,
    dashboard,
    distraction_blocker,
    focus,
    home,
    items as items_page,
    login as login_page,
    priorities,
    schedule,
    signup,
)


async def on_startup():
    print("INFO:     Initializing database...")
    init_db.init()
    print("INFO:     Database initialization complete.")


async def on_shutdown():
    print("INFO:     Application shutting down.")


app.on_startup(on_startup)
app.on_shutdown(on_shutdown)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router, tags=["login"])
app.include_router(blocker.router, tags=["blocker"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(items.router, prefix="/api/v1", tags=["items"])

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="UnCram · CS3203 Productivity",
        port=8000,
        storage_secret=settings.SECRET_KEY,
        reload=False,
        fastapi_docs=True,
        dark=True,
    )
