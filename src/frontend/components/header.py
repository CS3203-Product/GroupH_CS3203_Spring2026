from nicegui import ui


def create_header(left_drawer: ui.left_drawer, title: str) -> None:
    """App bar with UnCram branding."""
    with ui.header(elevated=True).classes(
        "items-center justify-between bg-gradient-to-r from-emerald-800 via-emerald-700 to-slate-900 shadow-md"
    ):
        with ui.row().classes("items-center gap-2"):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
                "flat round color=white"
            )
            ui.icon("eco", color="white", size="md")
            ui.label("UnCram").classes("text-h6 text-white font-bold tracking-tight")
            ui.label("·").classes("text-white text-opacity-50")
            ui.label(title).classes("text-subtitle1 text-emerald-100")
