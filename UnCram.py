<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
import time

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass
class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    pass

class FocusModeTimer:
    # This class is responsible for implementing a focus mode timer to help users stay focused on their tasks
    # We are creating a Pomodoro style timer
    # It breaks work into 25 minute "work" intervals with 5 minute breaks in between. 
    # After four "Pomodoros", the user takes a longer break of 15-30 minutes. Maybe we can let them set this one

    def __init__(self, work_min=25, break_min=5):
        self.work_sec = work_min * 60
        self.break_sec = break_min * 60
        self.reps = 0

    def start_session(self, duration, label="Work"):
        print(f"\n--- {label} Session Started ---")
        while duration > 0:
            mins, secs = divmod(duration, 60)
            # \r returns the cursor to the start of the line
            print(f"Time Remaining: {mins:02d}:{secs:02d}", end="\r")
            time.sleep(1)
            duration -= 1
        print(f"\n{label} session complete!")

    def run(self):
        try:
            while True:
                self.start_session(self.work_sec, "Work")
                self.reps += 1
                print(f"Total sessions completed: {self.reps}")
                
                self.start_session(self.break_sec, "Break")
        except KeyboardInterrupt:
            print("\nTimer stopped. Great work today!")

# --- Execution ---
if __name__ == "__main__":
    # You can now customize times easily when you create the object
    timer = FocusModeTimer(work_min=25, break_min=5)
    timer.run()

    pass

class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass
=======
import tkinter as tk

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass
class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    pass

class FocusModeTimer:
    # This class is responsible for implementing a focus mode timer to help users stay focused on their tasks
    # We are creating a Pomodoro style timer
    # It breaks work into 25 minute "work" intervals with 5 minute breaks in between. 
    # After four "Pomodoros", the user takes a longer break of 15-30 minutes. Maybe we can let them set this one

    def __init__(self, work_min=25, break_min=5):
        self.work_sec = work_min * 60
        self.break_sec = break_min * 60
        self.reps = 0
        self.current_time = 0
        self.running = False
        self.after_id = None

        self.window = tk.Tk()
        self.window.title("Go!")
        self.window.geometry("600x400+0+0")

        self.label = tk.Label(self.window, text="Ready?", font=("Comic Sans MS", 24))
        self.label.pack(pady=20)

        # Start and timer share the same frame
        stack = tk.Frame(self.window, width=300, height=150)
        stack.pack(pady=50)
        stack.pack_propagate(False)

        self.timer_text = tk.Label(stack, text="00:00", font=("Comic Sans MS", 48))
        self.timer_text.place_forget()

        self.start_button = tk.Button(stack, text="Start", command=self.start_work, font=("Comic Sans MS", 30))
        self.start_button.place(x=70, y=0)
        
        self.pause_button = tk.Button(stack, text="Pause", command=self.pause, font=("Comic Sans MS", 12))
        self.pause_button.place_forget
        self.continue_button = tk.Button(stack, text="Continue", command=self.cont, font=("Comic Sans MS", 12))
        self.continue_button.place_forget
        self.reset_button = tk.Button(stack, text="End timer", command=self.stop, font=("Comic Sans MS", 12))
        self.reset_button.place_forget

        self.window.mainloop()

    def start_work(self):
        if not self.running:
            self.running = True
            self.current_time = self.work_sec
            self.label.config(text="Go!")
            self.label.place(x=0, y=0, width=600, height=60)

            self.timer_text.place(x=60, y=0)
            self.pause_button.place(x=60, y=100)
            self.reset_button.place(x=150, y=100)
            self.start_button.place_forget()
            
            self.countdown()

    def start_break(self):
        self.current_time = self.break_sec
        self.label.config(text="Break time!")
        self.label.place(x=0, y=0, width=600, height=60)


        self.countdown()

    def countdown(self):
        mins, secs = divmod(self.current_time, 60)
        self.timer_text.config(text=f"{mins:02d}:{secs:02d}")

        if self.running and self.current_time > 0:
            self.current_time -= 1
            self.after_id = self.window.after(1000, self.countdown)
            return

        if self.current_time == 0:
            if self.label.cget("text") == "Go!":
                self.label.place(x=0, y=0, width=600, height=60)


                self.reps += 1
                self.start_break()
            else:
                self.running = False
                self.label.config(text=f"Blocks finished: {self.reps}")
                self.label.place(x=0, y=0, width=600, height=60)



    def pause(self):        # should a pomodoro timer have a pause button?
        if self.running:
            self.running = False
            if self.after_id:
                self.window.after_cancel(self.after_id)

            self.label.config(text="Take a moment, we all need them", font=("Comic Sans MS", 20))
            self.label.place(x=0, y=0, width=600, height=60)

            self.continue_button.place(x=60, y=100)

    def cont(self):
        if not self.running:
            self.running = True
            self.label.config(text="Keep going!", font=("Comic Sans MS", 20))
            self.label.place(x=0, y=0, width=600, height=60)

            self.continue_button.place_forget()
            self.countdown()

    def stop(self):
        self.running = False
        if self.after_id:
            self.window.after_cancel(self.after_id)

        self.current_time = 0
        self.label.config(text="Ready?")
        self.label.place(x=0, y=0, width=600, height=60)

        self.timer_text.config(text="00:00")



# --- Execution ---
if __name__ == "__main__":
    # You can now customize times easily when you create the object
    timer = FocusModeTimer(break_min=5)

    pass

class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass
>>>>>>> cc3b565 (Work On Timer Buttons - Brittney 2/6 11:25 pm)
=======
from nicegui import ui

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass
class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    pass

class FocusModeTimer:
    # This class is responsible for implementing a focus mode timer to help users stay focused on their tasks
    # We are creating a Pomodoro style timer
    # It breaks work into 25 minute "work" intervals with 5 minute breaks in between. 
    # After four "Pomodoros", the user takes a longer break of 15-30 minutes. Maybe we can let them set this one

class FocusModeTimer:
    def __init__(self, work_min=25, break_min=5):
        self.work_sec = work_min * 60
        self.break_sec = break_min * 60
        self.time_left = self.work_sec
        self.is_running = False
        self.mode = "Work" # Start in Work mode
        
        # Build the UI
        with ui.card().classes('w-64 items-center'):
            self.label = ui.label(self.mode).classes('text-h6')
            self.timer_display = ui.label(self.format_time()).classes('text-h3 font-mono')
            
            with ui.row():
                self.start_btn = ui.button('Start', on_click=self.start)
                ui.button('Reset', on_click=self.reset, color='red-5')

        # This is the NiceGUI way to handle loops without freezing the UI
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

    def tick(self):
        if self.time_left > 0:
            self.time_left -= 1
        else:
            # Switch modes when timer hits zero
            if self.mode == "Work":
                ui.notify("Time for a break!")
                self.mode = "Break"
                self.time_left = self.break_sec
            else:
                ui.notify("Back to work!")
                self.mode = "Work"
                self.time_left = self.work_sec
        
        self.update_ui()

    def update_ui(self):
        self.timer_display.text = self.format_time()
        self.label.text = self.mode

    # Instantiate the UI
    ui.label('Uncram Productivity Suite').classes('text-h4')
    FocusModeTimer()

    ui.run()

class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass
>>>>>>> d180aec (Focus timer using NiceGUI now - Brittney 2/18 10:26 am)
=======
from nicegui import ui

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass
class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    pass

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
        
        with ui.card().classes('w-64 items-center shadow-lg'):
            self.label = ui.label(self.mode).classes('text-h6')
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

    def tick(self):
        if self.time_left > 0:
            self.time_left -= 1
        else:
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

# --- MAIN EXECUTION (Outdent these!) ---
ui.label('Uncram!').classes('text-h4 q-ma-md')
FocusModeTimer()


class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass

ui.run(title="Uncram Timer")
>>>>>>> 46d121d (Fixed a error where it wouldn't run - Brittney 2/18 10:57 am)
=======
from nicegui import ui, app

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass
class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    pass

class FocusModeTimer:
    # This class is responsible for implementing a focus mode timer to help users stay focused on their tasks
    # We are creating a Pomodoro style timer
    # It breaks work into 25 minute "work" intervals with 5 minute breaks in between. 
    # After four "Pomodoros", the user takes a longer break of 15-30 minutes. Maybe we can let them set this one


    def __init__(self, work_min=1, break_min=1, long_break_min=20):
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
                ui.button('Start Break', on_click=self.start_break_session, color='orange').props('round')
            
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

  
# --- MAIN EXECUTION (Outdent these!) ---
with ui.column().classes('absolute-center items-center'):
    ui.label('Uncram!').classes('text-h2 q-mb-md font-bold') # Made it bigger/bolder
    FocusModeTimer()



class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass


app.add_static_files('/sound', 'sound') 

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Uncram Timer")
>>>>>>> 22dcc41 (Update UX/UI)
=======
from nicegui import ui, app

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass
class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    pass

class FocusModeTimer:
    # This class is responsible for implementing a focus mode timer to help users stay focused on their tasks
    # We are creating a Pomodoro style timer
    # It breaks work into 25 minute "work" intervals with 5 minute breaks in between. 
    # After four "Pomodoros", the user takes a longer break of 15-30 minutes. Maybe we can let them set this one


    def __init__(self, work_min=1, break_min=5, long_break_min=20):
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
                ui.button('Start Break', on_click=self.start_break_session, color='orange').props('round')
            
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

  
# --- MAIN EXECUTION (Outdent these!) ---
with ui.column().classes('absolute-center items-center'):
    ui.label('Uncram!').classes('text-h2 q-mb-md font-bold') # Made it bigger/bolder
    FocusModeTimer()



class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass


app.add_static_files('/sound', 'sound') 

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Uncram Timer")
>>>>>>> 683ba24 (update break min)
=======
from nicegui import ui, app

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass
class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    pass

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

  
# --- MAIN EXECUTION (Outdent these!) ---
with ui.column().classes('absolute-center items-center'):
    ui.label('Uncram!').classes('text-h2 q-mb-md font-bold') # Made it bigger/bolder
    FocusModeTimer()



class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass


app.add_static_files('/sound', 'sound') 

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Uncram Timer")
>>>>>>> 65741e4 (Remove Start Break button - Brittney Situ 4/5/2026 1:34 am)
