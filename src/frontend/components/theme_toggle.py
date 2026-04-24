"""Persisted light/dark appearance via NiceGUI ``ui.dark_mode``."""

from __future__ import annotations

from nicegui import app, ui
from nicegui.elements.dark_mode import DarkMode

_STORAGE_KEY = "prefer_dark_mode"


def setup_user_dark_mode() -> DarkMode:
    """Bind Quasar dark mode to ``app.storage.user``; call once at the start of each page."""
    initial = app.storage.user.get(_STORAGE_KEY)
    if initial is None:
        initial = True
        app.storage.user[_STORAGE_KEY] = initial
    dm = ui.dark_mode(initial)
    dm.bind_value(app.storage.user, _STORAGE_KEY)
    return dm


def create_theme_toggle_button(dm: DarkMode, *, for_header: bool = False) -> ui.button:
    """Icon shows the mode you switch to (sun when dark, moon when light)."""

    def icon_for(is_dark: bool | None) -> str:
        return "light_mode" if is_dark else "dark_mode"

    btn = ui.button(icon=icon_for(dm.value), on_click=lambda: dm.set_value(not bool(dm.value))).props(
        "flat round"
    )
    if for_header:
        btn.classes("text-slate-800 dark:text-white")
    else:
        btn.props("color=primary")
    btn.tooltip("Toggle light / dark mode")

    def sync_icon() -> None:
        btn.props(f"icon={icon_for(dm.value)}")

    dm.on_value_change(lambda _: sync_icon())
    return btn
