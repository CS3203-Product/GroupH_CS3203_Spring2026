from nicegui import ui

class Task:               
    def __init__(self, name, due_day):
        self.name = name
        self.due_day = due_day
        self.importance = 0
    pass

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass

class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    def __init__(self):
        ui.label("Schedule - Basic Daily view").style(
            "font-family: 'Comic Sans MS'; font-size: 40px; color: black;"
        )
        self.error_label = ui.label("").style("color: red")

        # --- TABLE DATA ---
        self.columns = [ {'name': 'importance', 'label': 'Importance', 'field': 'importance'},
        {'name': 'sun', 'label': 'Sunday', 'field': 'sun'},
        {'name': 'mon', 'label': 'Monday', 'field': 'mon'},
        {'name': 'tues', 'label': 'Tuesday', 'field': 'tues'},
        {'name': 'wed', 'label': 'Wednesday', 'field': 'wed'},
        {'name': 'thur', 'label': 'Thursday', 'field': 'thur'},
        {'name': 'fri', 'label': 'Friday', 'field': 'fri'},
        {'name': 'sat', 'label': 'Saturday', 'field': 'sat'}, ]

        importance = list(range(0, 21))

        self.rows = [
            {'importance': str(t), 'sun': '', 'mon': '', 'tues': '', 'wed': '', 'thur': '', 'fri': '', 'sat': ''}
            for t in importance]
        self.tasks = []

        with ui.row():
            self.task_name_input = ui.input("Task name")
            self.day_input = ui.select(
                ["sun", "mon", "tues", "wed", "thur", "fri", "sat"],
                label="Due day" )
            self.importance_input = ui.number("Importance (0–20)", min=0, max=20, value=0)
            ui.button("Add Task", on_click=self.add_task)
            
        self.table = ui.table(columns=self.columns, rows=self.rows)

    def add_task(self):
        name = self.task_name_input.value
        day = self.day_input.value
        importance = self.importance_input.value
            
        if not name or not day:
            self.error_label.text = ("Please enter a task name and select a day.")
            return
        else:
            self.error_label.text = ""
            
        new_task = Task(name, day)
        new_task.importance = int(importance)
        self.tasks.append(new_task)

        self.populate_calendar()
        self.table.update() 

        self.task_name_input.value = ""
        self.day_input.value = None
        self.importance_input.value = 0

    def populate_calendar(self):
        for row in self.rows:
            for day in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
                row[day] = ""
            
        for task in self.tasks:
                target_row = self.rows[task.importance]
                if target_row[task.due_day]:
                    target_row[task.due_day] += f", {task.name}"
                else:
                    target_row[task.due_day] = task.name
        self.table.rows = self.rows

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
    # This class is responsible for blocking other websites from being accessed when task sessions begin.

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass


TimeBlockingScheduler()
ui.run()