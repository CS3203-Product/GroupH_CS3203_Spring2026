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


        # CWE-252 Concept: Verify the UI component is actually active 
        # before changing the internal boolean state.
        
        #try:
            #self.is_running = not self.is_running
            #self.tick_timer.active = self.is_running
            
            # Verify the timer actually switched state
            #if self.tick_timer.active != self.is_running:
                # If they don't match, the timer 'engine' failed to respond
                #raise ValueError("Timer Engine Mismatch")
                
            #elf.start_btn.text = "Pause" if self.is_running else "Resume"
            
        #except Exception as e:
            # Revert state to keep app consistent (Rollback)
            #self.is_running = False
            #self.tick_timer.active = False
            #ui.notify("System Error: Could not toggle timer.", type='warning')

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

            # --- CWE-252 FIX: CHECK RETURN VALUE ---
            # Instead of just calling self.alarm.play(), we should ideally
            # verify the state. Since NiceGUI audio is client-side, we wrap
            # critical actions in a way that handles failures.
           # try:
                #self.alarm.play()
                # If we had a backend analytics call here:
                # result = db.save_session(self.mode)
                # if not result: raise Exception("Data not saved")

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


class FocusTaskTimer:
    """Count-up task timer using the same visual style as the Focus Mode timer."""

    def __init__(
        self,
        *,
        task_title: str,
        started_at,
        on_complete=None,
        compact: bool = False,
    ):
        from datetime import datetime

        self.task_title = task_title
        self.started_at = started_at or datetime.utcnow()
        self.on_complete = on_complete
        self.is_running = True

        card_classes = "w-full items-center shadow-lg p-5"
        if compact:
            card_classes = "w-full items-center shadow-md p-4 bg-slate-50 dark:bg-slate-900"

        with ui.card().classes(card_classes):
            ui.label("Task timer").classes("text-xs uppercase tracking-wide text-slate-500")
            self.label = ui.label(task_title).classes("text-h6 font-bold text-center")
            self.timer_display = ui.label(self.format_elapsed()).classes(
                "text-h3 font-mono text-blue-600"
            )
            self.status = ui.label("Focus session running").classes(
                "text-caption text-slate-600 dark:text-slate-300"
            )

            with ui.row().classes("gap-2 justify-center"):
                self.pause_btn = ui.button("Pause", on_click=self.toggle).props(
                    "color=primary outline"
                )
                if on_complete is not None:
                    ui.button(
                        "Complete task",
                        icon="task_alt",
                        on_click=on_complete,
                    ).props("color=positive elevated")

        self.tick_timer = ui.timer(1.0, self.tick, active=True)

    def elapsed_seconds(self) -> int:
        from datetime import datetime

        try:
            return max(0, int((datetime.utcnow() - self.started_at).total_seconds()))
        except TypeError:
            return 0

    def format_elapsed(self) -> str:
        total_seconds = self.elapsed_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def toggle(self) -> None:
        self.is_running = not self.is_running
        self.tick_timer.active = self.is_running
        self.pause_btn.text = "Pause" if self.is_running else "Resume"
        self.status.text = "Focus session running" if self.is_running else "Timer display paused"

    def tick(self) -> None:
        self.timer_display.text = self.format_elapsed()

