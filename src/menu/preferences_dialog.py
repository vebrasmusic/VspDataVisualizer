''' holds the layout for the preferences dialog window '''
from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
    QDialog,
    QGroupBox,
    QGridLayout
)
from src.menu.preferences import PreferenceChanges, Preferences
from src.menu.ui import PreferenceLineEdit

class PreferencesDialog(QDialog):
    ''' dialog for setting preferences '''
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences")
        self.changes = {}
        self.setup_ui()

    def setup_ui(self):
        ''' lays out the UI for the dialog '''
        prefs = Preferences()
        # Create buttons
        self.accept_button = QPushButton("Save Changes")
        self.cancel_button = QPushButton("Cancel")

        self.calibration_text = QLabel("Calibration is of the form bx + c. This curve is used for QA comparison.")
        self.slope_label = QLabel("Slope (b):")
        self.y_int_label = QLabel("Y intercept (c):")
        self.r_squared_label = QLabel("R^2:")

        slope = prefs.get_preference("calibration_parameters", "slope")
        y_intercept = prefs.get_preference("calibration_parameters", "y_intercept")
        r_squared = prefs.get_preference("calibration_parameters", "r_squared")
        self.slope_input = PreferenceLineEdit(slope, "calibration_parameters", "slope")
        self.y_intercept_input = PreferenceLineEdit(y_intercept,"calibration_parameters", "y_intercept")
        self.r_squared_input = PreferenceLineEdit(r_squared, "calibration_parameters", "r_squared")

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

        # create a GroupBox to section off certain preference sections

        self.rpd_label = QLabel("RPD (relative percent difference) minimum threshold (%) for both slope and y-int. used for QA checking between master and measured curves.")
        self.slope_rpd_label = QLabel("Slope RPD Threshhold (%)")
        self.y_int_rpd_label = QLabel("Y intercept RPD Threshhold (%)")
        

        slope_rpd = prefs.get_preference("qa_parameters", "slope_rpd")
        y_intercept_rpd = prefs.get_preference("qa_parameters", "y_intercept_rpd")
        self.slope_rpd_input = PreferenceLineEdit(slope_rpd, "qa_parameters", "slope_rpd")
        self.y_intercept_rpd_input = PreferenceLineEdit(y_intercept_rpd, "qa_parameters", "y_intercept_rpd")


        self.qa_group_box = QGroupBox("QA Parameters")
        self.qa_group_layout = QGridLayout()
        self.qa_group_box.setLayout(self.qa_group_layout)

        self.qa_group_layout.addWidget(self.rpd_label)
        self.qa_group_layout.addWidget(self.slope_rpd_label)
        self.qa_group_layout.addWidget(self.slope_rpd_input)
        self.qa_group_layout.addWidget(self.y_int_rpd_label)
        self.qa_group_layout.addWidget(self.y_intercept_rpd_input)


        # Create and set layout
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        # Add widgets to layout
        self.main_layout.addWidget(self.calibration_group_box)
        self.main_layout.addWidget(self.qa_group_box)
        self.main_layout.addWidget(self.accept_button)
        self.main_layout.addWidget(self.cancel_button)


        # Connect signals
        self.accept_button.clicked.connect(self.apply_changes_to_preferences)
        self.cancel_button.clicked.connect(self.reject)

    def apply_changes_to_preferences(self):
        ''' applies any changes made in dialog window '''
        # Example method to save preferences

        self.accept()
        
        prefs = Preferences()
        pref_changes = PreferenceChanges()
        for category, key in pref_changes.changes.items():
            for key, value in pref_changes.changes[category].items():
                prefs.preferences[category][key] = value
        prefs.save_preferences()
        pref_changes.initialize() # reset the changes thing