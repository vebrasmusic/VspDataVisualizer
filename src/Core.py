''' handles the core functionality tying together the menu and the analysis '''
from src.menu import MainMenu

class Core():
    ''' ties together the menu and analyses '''
    def __init__(self):
        self.menu = MainMenu()

    def run(self):
        ''' runs the app '''
        self.menu.run()