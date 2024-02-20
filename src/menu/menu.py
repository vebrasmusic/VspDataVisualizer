''' menu core, ties together ui and function layout for the menu '''
from PyQt6.QtWidgets import QApplication
from src.menu.main_window import MainWindow

class MainMenu():
    ''' main menu for the app, core that ties together ui and logic '''
    def __init__(self):
        self.app = QApplication([]) #creates the application, need one of these per app
        self.window = MainWindow()

    def run(self):
        ''' runs the application '''
        self.app.exec() #runs the application's event loop
