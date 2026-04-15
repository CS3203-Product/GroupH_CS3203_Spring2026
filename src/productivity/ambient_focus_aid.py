"""Simple ambient audio controls (streamed sample)."""

from nicegui import ui


class AmbientFocusAid:
    def __init__(self) -> None:
        self.audio = ui.audio(
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        )

        with ui.row().classes("gap-2"):
            ui.button("Play", on_click=self.audio.play).props("color=primary")
            ui.button("Pause", on_click=self.audio.pause).props("outline")
            ui.button("Jump to 0:30", on_click=lambda: self.audio.seek(30)).props(
                "flat"
            )
