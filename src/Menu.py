''' handles the ui for the app '''
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFileDialog,
    QDialogButtonBox,
    QLabel
)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    ''' main window for the app '''
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VSP Analyzer (Lactate)")

        button1 = QPushButton("Select Data Folder")
        button1.clicked.connect(self.select_folder) #set where the signal goes form the button press


        layout = QVBoxLayout()

        widget = QWidget()

        layout.addWidget(button1)

        widget.setLayout(layout)

        self.setFixedSize(QSize(800, 600))

        # Set the central widget of the Window.
        self.setCentralWidget(button1)

    def select_folder(self):
        ''' opens a dialog to select the data folder '''

        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        if dlg.exec():
            filenames = dlg.selectedFiles()
            print(filenames) #this is a list of the selected files, in this case just a folder

class MainMenu():
    ''' main menu for the app '''
    def __init__(self):
        self.app = QApplication([]) #creates the application, need one of these per app
        self.window = MainWindow()
        self.window.show() #they do not show by default

    def run(self):
        self.app.exec() #runs the application's event loop
