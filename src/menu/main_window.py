''' handles the ui for the app '''
from PyQt6.QtCore import QSize 
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from src.analysis.analysis import AnalysisCore
from src.menu.ui import (
    FileUploadButton,
    AxisSelectDropdown,
    AxisSelectLabel,
    AnalysisTypeDropdown,
    AnalysisTypeLabel,
    LCD, 
    SelectedFileText,
    StartAnalysisButton
)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    ''' main window for the app '''
    def __init__(self):
        super().__init__()
        self.upload_button = FileUploadButton()
        self.axis_select_label = AxisSelectLabel()
        self.axis_select_dropdown = AxisSelectDropdown()
        self.analysis_type_label = AnalysisTypeLabel()
        self.analysis_type_dropdown = AnalysisTypeDropdown()
        self.start_analysis_button = StartAnalysisButton()
        self.selected_folder_text = SelectedFileText()
        self.slope_lcd = LCD()
        self.int_lcd = LCD()
        self.r_squared_lcd = LCD()
        self.create_ui_layout() # this actually makes all the UI
        self.add_graph_layout()  # Call a new method to add the graph layout

    def create_ui_layout(self):
        ''' creates the ui layout '''
        self.show()
        self.analysis_type_dropdown.activated.connect(self.update_layout_axis_selection)
        self.upload_button.clicked.connect(self.update_layout_file_selection)
        self.start_analysis_button.start_signal.connect(self.start_analysis)
        self.setWindowTitle("TRAQ Calibration Analyzer")
        self.setMinimumSize(QSize(1200, 800))

        self.main_layout = QVBoxLayout()  # Main layout for side-by-side arrangement
        widget = QWidget()

        # Create a QVBoxLayout for the label and dropdown to stack them vertically
        self.axis_layout = QVBoxLayout()
        self.axis_layout.addWidget(self.axis_select_label)
        self.axis_layout.addWidget(self.axis_select_dropdown)

        # make div for the analysis type selecter and label
        self.analysis_type_layout = QVBoxLayout()
        self.analysis_type_layout.addWidget(self.analysis_type_label)
        self.analysis_type_layout.addWidget(self.analysis_type_dropdown)

        self.upload_button_layout = QVBoxLayout()
        self.upload_button_layout.addWidget(self.upload_button)
        self.upload_button_layout.addWidget(self.selected_folder_text)
        # Add the upload button to the main layout
        

        # top left div
        self.top_left_layout = QVBoxLayout()
        self.top_left_layout.addWidget(self.start_analysis_button)
        self.top_left_layout.addLayout(self.upload_button_layout)
        self.top_left_layout.addLayout(self.analysis_type_layout)
        self.top_left_layout.addLayout(self.axis_layout)

        #top right div
        self.top_right_layout = QVBoxLayout()
        self.top_right_layout.addWidget(self.slope_lcd)
        self.top_right_layout.addWidget(self.int_lcd)
        self.top_right_layout.addWidget(self.r_squared_lcd)

        # top div (contains left and right)
        self.top_layout = QHBoxLayout()
        self.top_layout.addLayout(self.top_left_layout)
        self.top_layout.addLayout(self.top_right_layout)


        self.main_layout.addLayout(self.top_layout)
        #graph layout is under this as well

        widget.setLayout(self.main_layout)
        # Set the central widget of the Window to the widget containing the layout
        self.setCentralWidget(widget)

    def start_analysis(self):
        ''' starts the analysis '''
        #set vars
        if self.upload_button.selected_folder is not None:
            directory = self.upload_button.selected_folder
        else:
            raise ValueError("No directory selected")
        analysis_type = self.analysis_type_dropdown.selected_analysis_type
        axis_order_in_file = self.axis_select_dropdown.axis_order

        analysis_core = AnalysisCore(directory, analysis_type, axis_order_in_file)
        fig1, ax1, fig2, ax2, measured_line, qa_checks = analysis_core.run()
        self.update_graphs(fig1, fig2)
        self.update_lcd_metrics(measured_line.slope, measured_line.y_intercept, measured_line.r_squared)

    def update_lcd_metrics(self, slope, y_intercept, r_squared):
        ''' updates the metrics '''
        self.slope_lcd.display(slope)
        self.int_lcd.display(y_intercept)
        self.r_squared_lcd.display(r_squared)

    def update_layout_file_selection(self):
        ''' Updates the layout based on the analysis type selection '''
        # Instead of removing and re-adding widgets, we show or hide them based on the condition
        if self.upload_button.selected_folder is not None:
            self.selected_folder_text.setText(f"Data folder selected: {self.upload_button.selected_folder}")
            self.selected_folder_text.setVisible(True)
        else:
            self.selected_folder_text.setVisible(False)
    
    def update_layout_axis_selection(self):
        ''' Updates the layout based on the analysis type selection '''
        # Instead of removing and re-adding widgets, we show or hide them based on the condition
        if self.analysis_type_dropdown.selected_analysis_type == "LactateVSPCalibration":
            self.axis_select_dropdown.setDisabled(False)
        else:
            self.axis_select_dropdown.setDisabled(True)


    def add_graph_layout(self):
        ''' Adds a layout for displaying graphs '''
        self.graph_layout = QHBoxLayout()  # Create a new vertical layout for graphs

        # First graph
        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.graph_layout.addWidget(self.canvas1)

        # Second graph
        self.figure2 = Figure()
        self.canvas2 = FigureCanvas(self.figure2)
        self.graph_layout.addWidget(self.canvas2)

        # Add the graph layout to the main layout
        self.main_layout.addLayout(self.graph_layout)

    def update_graphs(self, fig1, fig2):
        ''' updates the graphs with the new figures '''
        # Remove the old canvas widgets from the layout
        self.graph_layout.removeWidget(self.canvas1)
        self.canvas1.deleteLater()
        self.graph_layout.removeWidget(self.canvas2)
        self.canvas2.deleteLater()

        # Update the figures
        self.figure1 = fig1
        self.figure2 = fig2

        # Create new canvas widgets with the updated figures
        self.canvas1 = FigureCanvas(self.figure1)
        self.graph_layout.addWidget(self.canvas1)
        self.canvas2 = FigureCanvas(self.figure2)
        self.graph_layout.addWidget(self.canvas2)