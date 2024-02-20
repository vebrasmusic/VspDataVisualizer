''' handles the ui for the app '''
from PyQt6.QtWidgets import QApplication
from src.menu.main_window import MainWindow

class MainMenu():
    ''' main menu for the app '''
    def __init__(self):
        self.app = QApplication([]) #creates the application, need one of these per app
        self.window = MainWindow()

    def run(self):
        ''' runs the application '''
        self.app.exec() #runs the application's event loop
