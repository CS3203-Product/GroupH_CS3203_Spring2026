from nicegui import ui
from Task import Task

class TaskPrioritizationEngine:
    def __init__(self):
        self.selected_day = 'Monday' # Default
        
        with ui.row().classes('w-full justify-between items-start flex-nowrap'):
            self.container = ui.column().classes('space-y-2 w-2/3')

            with ui.column().classes('items-start w-1/3 self-start'):
                self.input_field = ui.input(placeholder='Add a task...')
                
                # Store reference to button so we can change its text
                with ui.dropdown_button('Due: ...') as self.day_btn:
                    ui.item('Day 1', on_click=lambda: self.update_selection('Day 1'))
                    ui.item('Day 2', on_click=lambda: self.update_selection('Day 2'))
                
                ui.button('Add', on_click=self.add_task)

    # Move this outside __init__
    def update_selection(self, day):
        self.selected_day = day
        self.day_btn.set_text(f'Due: {day}')


    def add_task(self, _):
        text = self.input_field.value.strip()
        if not text:
            return
        
        new_task = Task(text, self.selected_day)
        print(f"Created task: {new_task.name} for {new_task.due_day}")
        
        with self.container:
            task_frame = ui.column().classes('p-2 border rounded')

            with task_frame:
                task_label = ui.label(text).classes('flex-grow')
                task_input = ui.input(value=text).classes('flex-grow')
                task_input.visible = False

                edit_button = ui.button('Edit')
                save_button = ui.button('Save')
                cancel_button = ui.button('Cancel')
                delete_button = ui.button('Delete').classes('text-red-600')

                save_button.visible = False
                cancel_button.visible = False

                delete_button.on_click(lambda _, f=task_frame: f.delete())

                def start_edit():
                    task_label.visible = False
                    task_input.visible = True
                    edit_button.visible = False
                    save_button.visible = True
                    cancel_button.visible = True

                edit_button.on_click(lambda _: start_edit())

                def save_changes():
                    new_text = task_input.value.strip()
                    if new_text:
                        task_label.text = new_text
                    task_label.visible = True
                    task_input.visible = False
                    edit_button.visible = True
                    save_button.visible = False
                    cancel_button.visible = False

                save_button.on_click(lambda _: save_changes())

                def cancel_edit():
                    task_input.value = task_label.text
                    task_label.visible = True
                    task_input.visible = False
                    edit_button.visible = True
                    save_button.visible = False
                    cancel_button.visible = False

                cancel_button.on_click(lambda _: cancel_edit())

        self.input_field.value = ''
        self.input_field.focus()

app = TaskPrioritizationEngine()
ui.run()
