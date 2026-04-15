from nicegui import ui

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    def __init__(self):
        self.a = ui.audio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3')

        ui.button('Play', on_click=self.a.play)
        ui.button('Pause', on_click=self.a.pause)
        ui.button('Jump to 0:30', on_click=lambda: self.a.seek(30))

app = AmbientFocusAid()
ui.run()

