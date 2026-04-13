from nicegui import ui

class Login:
<<<<<<< HEAD
    
    pass
=======

    credentials = {
        "alice": "123",
        "bob": "password",
        "charlie": "abc",
    }

    def __init__(self):
        ui.label('Log In or Create An Account').style('font-size: 24px; font-weight: bold;')
        ui.label('This product is still under development and creating an account is not yet supported.').style('color: #FF0000; font-size: 16px; font-weight: bold;')
        ui.label('Please log in using one of the demo accounts: alice, bob, or charlie')

        self.username_input = ui.input("Username")
        self.password_input = ui.input("Password", password=True)

        ui.button("Login", on_click=self.try_login)

    def try_login(self):
        username = self.username_input.value
        password = self.password_input.value

        if username not in self.credentials or self.credentials[username] != password:
            ui.notify("Username or password is incorrect")
            return

        ui.notify("Login successful")

Login()
ui.run()
>>>>>>> bae37f7 (Made login screen -Brittney 4/13/2026 1:07 pm)
