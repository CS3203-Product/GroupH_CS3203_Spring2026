"""Pomodoro-style focus timer for NiceGUI."""

from nicegui import ui


class FocusModeTimer:
    def __init__(self, work_min: int = 1, break_min: int = 5, long_break_min: int = 20):
        self.work_sec = work_min * 60
        self.break_sec = break_min * 60
        self.long_break_sec = long_break_min * 60

        self.time_left = self.work_sec
        self.is_running = False
        self.mode = "Work"
        self.completed_pomodoros = 0
        self.alarm = ui.audio("/assets/sound/alarm.mp3").classes("hidden")

        with ui.card().classes("w-full max-w-md items-center shadow-lg p-6"):
            self.label = ui.label(self.mode).classes("text-h6 font-bold")
            self.timer_display = ui.label(self.format_time()).classes(
                "text-h3 font-mono"
            )

            with ui.row().classes("gap-2"):
                self.start_btn = ui.button("Start", on_click=self.start).props(
                    "color=primary elevated"
                )
                ui.button("Reset", on_click=self.reset, color="red").props("outline")

            self.stats = ui.label(f"Pomodoros: {self.completed_pomodoros}").classes(
                "text-caption text-slate-600"
            )

        self.tick_timer = ui.timer(1.0, self.tick, active=False)

    def format_time(self) -> str:
        mins, secs = divmod(self.time_left, 60)
        return f"{mins:02d}:{secs:02d}"

    def start(self) -> None:
        self.is_running = not self.is_running
        self.tick_timer.active = self.is_running
        self.start_btn.text = "Pause" if self.is_running else "Resume"

    def reset(self) -> None:
        self.is_running = False
        self.tick_timer.active = False
        self.time_left = self.work_sec
        self.mode = "Work"
        self.update_ui()
        self.start_btn.text = "Start"

    def tick(self) -> None:
        if self.time_left > 0:
            self.time_left -= 1
        else:
            self.alarm.play()
            if self.mode == "Work":
                self.completed_pomodoros += 1
                if self.completed_pomodoros % 4 == 0:
                    self.mode = "Long Break"
                    self.time_left = self.long_break_sec
                    ui.notify(
                        "Amazing! Four sessions done — take a long break.",
                        type="positive",
                    )
                else:
                    self.mode = "Break"
                    self.time_left = self.break_sec
                    ui.notify("Short break time.")
            else:
                self.mode = "Work"
                self.time_left = self.work_sec
                ui.notify("Back to work.")

        self.update_ui()

    def update_ui(self) -> None:
        self.timer_display.text = self.format_time()
        self.label.text = self.mode
        self.stats.text = f"Pomodoros: {self.completed_pomodoros}"
        if self.mode == "Work":
            self.timer_display.classes("text-blue-600", remove="text-orange-500")
        else:
            self.timer_display.classes("text-orange-500", remove="text-blue-600")
