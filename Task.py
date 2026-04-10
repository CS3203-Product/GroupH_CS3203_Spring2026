class Task:                 # Task class; it will be easier for the TimeBlockSched to access tasks with a task class
    def __init__(self, name, due_day):
        self.name = name
        self.due_day = due_day
        self.importance = 0
    pass