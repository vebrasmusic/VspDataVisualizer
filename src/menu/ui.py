''' defines all ui elements for the menu '''
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QPushButton,
    QFileDialog,
    QComboBox,
    QLabel,
    QLCDNumber,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QLineEdit,
    QGridLayout
)
from src.menu.preferences import Preferences

class AnalysisTypeDropdown(QComboBox):
    ''' dropdown for selecting the axis order in the file '''
    def __init__(self):
        super().__init__()
        self.selected_analysis_type = "Lactate VSP Calibration" #this is the type that determines analysis in Core
        self.addItem("Lactate VSP Calibration")
        self.addItem("Lactate Stone Calibration")
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
        super().__init__("Selected file:")

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

class PreferencesDialog(QDialog):
    ''' dialog for setting preferences '''
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences")
        self.setup_ui()

    def setup_ui(self):
        ''' lays out the UI for the dialog '''
        # Create buttons
        self.accept_button = QPushButton("Save Changes")
        self.cancel_button = QPushButton("Cancel")

        self.calibration_text = QLabel("Calibration is of the form bx + c. This curve is used for QA comparison.")
        self.slope_label = QLabel("Slope (b):")
        self.y_int_label = QLabel("Y intercept (c):")
        self.r_squared_label = QLabel("R^2:")

        prefs = Preferences()
        slope = prefs.get_preference("calibration_parameters", "slope")
        y_intercept = prefs.get_preference("calibration_parameters", "y_intercept")
        r_squared = prefs.get_preference("calibration_parameters", "r_squared")
        self.slope_input = QLineEdit(slope)
        self.y_intercept_input = QLineEdit(y_intercept)
        self.r_squared_input = QLineEdit(r_squared)

        # create a GroupBox to section off certain preference sections
        self.calibration_group_box = QGroupBox("Master Calibration Curve")
        self.calibration_group_layout = QGridLayout()
        self.calibration_group_box.setLayout(self.calibration_group_layout)

        self.calibration_group_layout.addWidget(self.calibration_text)
        self.calibration_group_layout.addWidget(self.slope_label)
        self.calibration_group_layout.addWidget(self.slope_input)
        self.calibration_group_layout.addWidget(self.y_int_label)
        self.calibration_group_layout.addWidget(self.y_intercept_input)
        self.calibration_group_layout.addWidget(self.r_squared_label)
        self.calibration_group_layout.addWidget(self.r_squared_input)

        # Create and set layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Add widgets to layout
        self.main_layout.addWidget(self.calibration_group_box)
        self.main_layout.addWidget(self.accept_button)
        self.main_layout.addWidget(self.cancel_button)


        # Connect signals
        self.accept_button.clicked.connect(self.apply_changes_to_preferences)
        self.cancel_button.clicked.connect(self.reject)

    def apply_changes_to_preferences(self):
        ''' applies any changes made in dialog window '''
        # Example method to save preferences
        slope = self.slope_input.text()
        y_intercept = self.y_intercept_input.text()
        r_squared = self.r_squared_input.text()
        self.accept()
        
        # Assuming apply_changes_to_preferences is a method to save these preferences
        changes = {
            "calibration_parameters": {
                "slope": slope,
                "y_intercept": y_intercept,
                "r_squared": r_squared
            }
        }

        prefs = Preferences()
        for key, value in changes.items():
            prefs.preferences[key] = value
        prefs.save_preferences()  

class SaveDialog(QFileDialog):
    ''' dialog for saving the file '''
    def __init__(self):
        super().__init__()
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.setLabelText(QFileDialog.DialogLabel.LookIn, "Save to:")
        self.setLabelText(QFileDialog.DialogLabel.FileName, "File name:")
        self.setLabelText(QFileDialog.DialogLabel.Accept, "Save")
        self.setLabelText(QFileDialog.DialogLabel.Reject, "Cancel")
        self.setLabelText(QFileDialog.DialogLabel.FileType, "File type:")
        self.setDefaultSuffix("json")
