''' defines all ui elements for the menu '''
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QPushButton,
    QFileDialog,
    QComboBox,
    QLabel,
    QLCDNumber,
    QMessageBox
)

class AnalysisTypeDropdown(QComboBox):
    ''' dropdown for selecting the axis order in the file '''
    def __init__(self):
        super().__init__()
        self.selected_analysis_type = "LactateVSPCalibration" #this is the type that determines analysis in Core
        self.addItem("LactateVSPCalibration")
        self.addItem("LactateStoneCalibration")
        self.activated.connect(self.on_change)

    def on_change(self):
        ''' called when the dropdown is changed '''
        if self.currentIndex() == 0:
            self.selected_analysis_type = "LactateVSPCalibration"
        elif self.currentIndex() == 1:
            self.selected_analysis_type = "LactateStoneCalibration"

class AnalysisTypeLabel(QLabel):
    ''' label for the axis select dropdown '''
    def __init__(self):
        super().__init__()
        self.setText("Analysis type:")

class StartAnalysisButton(QPushButton):
    ''' button for starting the analysis '''

    start_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setText("Start Analysis")
        self.clicked.connect(self.emit_start_signal)

    def emit_start_signal(self):
        ''' emits the start signal '''
        self.start_signal.emit()

class AxisSelectDropdown(QComboBox):
    ''' dropdown for selecting the axis order in the file '''
    def __init__(self):
        super().__init__()
        self.axis_order = ('current', 'time') #this tuple gets passed ALLLL the way to the analysis
        self.addItem("Current | Time")
        self.addItem("Time | Current")
        self.activated.connect(self.on_change)

    def on_change(self):
        ''' called when the dropdown is changed '''
        if self.currentIndex() == 0:
            self.axis_order = ('current', 'time') 
        elif self.currentIndex() == 1:
            self.axis_order = ('time', 'current')

class AxisSelectLabel(QLabel):
    ''' label for the axis select dropdown '''
    def __init__(self):
        super().__init__()
        self.setText("Select the axis order in the file")

class SelectedFileText(QLabel):
    ''' label for the axis select dropdown '''
    def __init__(self):
        super().__init__()

class FileUploadButton(QPushButton):
    ''' button for uploading the data folder '''

    def __init__(self):
        super().__init__()
        self.selected_folder = None
        self.setText("Select Data Folder")
        self.clicked.connect(self.select_folder) #set where the signal goes form the button press
    
    def select_folder(self):
        ''' opens a dialog to select the data folder '''
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        if dlg.exec():
            filenames = dlg.selectedFiles()
            # Call StartAnalysis with the first selected directory
            self.selected_folder = filenames[0] # stores filename into the object

class LCD(QLCDNumber):
    ''' lcd for displaying the metrics '''
    def __init__(self):
        super().__init__()
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.setDigitCount(8)

class Alert(QMessageBox):
    ''' alert for displaying errors '''
    def __init__(self, parameter: str, value: float):
        super().__init__()
        self.setText("QA Not Passed")
        self.setInformativeText(f"The parameter {parameter} with value {value} is outside the acceptable QA bounds. I recommend not shipping this batch.")
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setIcon(QMessageBox.Icon.Critical)
