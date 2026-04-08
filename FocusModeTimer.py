from nicegui import ui, app

class FocusModeTimer:
    # This class is responsible for implementing a focus mode timer to help users stay focused on their tasks
    # We are creating a Pomodoro style timer
    # It breaks work into 25 minute "work" intervals with 5 minute breaks in between. 
    # After four "Pomodoros", the user takes a longer break of 15-30 minutes. Maybe we can let them set this one

    def __init__(self, work_min=25, break_min=5, long_break_min=20):
        self.work_sec = work_min * 60
        self.break_sec = break_min * 60
        self.long_break_sec = long_break_min * 60
        
        self.time_left = self.work_sec
        self.is_running = False
        self.mode = "Work"
        self.completed_pomodoros = 0 # Track for long breaks
        self.alarm = ui.audio('sound/alarm.mp3').classes('hidden')
        
        # Build the UI
        with ui.card().classes('w-80 items-center shadow-lg'):
            self.label = ui.label(self.mode).classes('text-h6 font-bold')
            self.timer_display = ui.label(self.format_time()).classes('text-h3 font-mono')
            
            with ui.row():
                self.start_btn = ui.button('Start', on_click=self.start).props('elevated')
                ui.button('Reset', on_click=self.reset, color='red-5').props('outline')
            
            # Counter display
            self.stats = ui.label(f'Pomodoros: {self.completed_pomodoros}').classes('text-caption')

        self.tick_timer = ui.timer(1.0, self.tick, active=False)

    def format_time(self):
        mins, secs = divmod(self.time_left, 60)
        return f"{mins:02d}:{secs:02d}"

    def start(self):
        self.is_running = not self.is_running
        self.tick_timer.active = self.is_running
        self.start_btn.text = 'Pause' if self.is_running else 'Resume'

    def reset(self):
        self.is_running = False
        self.tick_timer.active = False
        self.time_left = self.work_sec
        self.mode = "Work"
        self.update_ui()
        self.start_btn.text = 'Start'

    def start_break_session(self):
        if self.mode == "Work":
            self.is_running = False
            self.tick_timer.active = False
            self.mode = "Break"
            self.time_left = self.break_sec
            self.update_ui()
            ui.notify("Break time! Relax for a bit.")
        else:
            ui.notify("You are already on a break!")

    def tick(self):
        if self.time_left > 0:
            self.time_left -= 1
        else:
            self.alarm.play()  # Play alarm sound when timer ends
            if self.mode == "Work":
                self.completed_pomodoros += 1
                if self.completed_pomodoros % 4 == 0:
                    self.mode = "Long Break"
                    self.time_left = self.long_break_sec
                    ui.notify("Amazing! 4 sessions done. Take a long break!", type='positive')
                else:
                    self.mode = "Break"
                    self.time_left = self.break_sec
                    ui.notify("Time for a short break!")
            else:
                self.mode = "Work"
                self.time_left = self.work_sec
                ui.notify("Back to work!")
        
        self.update_ui()


    def update_ui(self):
        self.timer_display.text = self.format_time()
        self.label.text = self.mode
        self.stats.text = f'Pomodoros: {self.completed_pomodoros}'
    
    # Change card color based on mode
        if self.mode == "Work":
            self.timer_display.classes('text-blue-500', remove='text-orange-500')
        else:
            self.timer_display.classes('text-orange-500', remove='text-blue-500')


with ui.column().classes('absolute-center items-center'):
    ui.label('Uncram!').classes('text-h2 q-mb-md font-bold') # Made it bigger/bolder
    FocusModeTimer()

app.add_static_files('/sound', 'sound') 

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
