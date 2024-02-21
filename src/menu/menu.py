''' menu core, ties together ui and function layout for the menu '''
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.menu.main_window import MainWindow

class MainMenu():
    ''' main menu for the app, core that ties together ui and logic '''
    def __init__(self):
        self.app = QApplication([]) #creates the application
        self.app.setApplicationName('TRAQ Sensor QA') #sets the application name
        self.app.setApplicationDisplayName('TRAQ Sensor QA') #sets the application display name
        self.app.setWindowIcon(QIcon('assets/icon.png')) #sets the application icon
        self.window = MainWindow()

    def run(self):
        ''' runs the application '''
        self.app.exec() #runs the application's event loop
