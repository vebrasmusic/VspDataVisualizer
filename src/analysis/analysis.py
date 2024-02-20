''' handles the analysis of the data '''
from abc import ABC, abstractmethod
import json
import numpy
import matplotlib.pyplot as plt
from scipy.stats import linregress

from src.analysis.data import Data

'''
Hows this work?

Top level, you have an Analysis, which will run a specific type of analysis / plot data.
An Analysis has a Data object
A Data object has a list of Run objects
A Run can contain different kinds of TextLoader or ConcentrationParser.
'''

class Analysis(ABC):
    ''' can have a figure, and some rules etc.abs '''
    # data will ave a couple analyses
    @abstractmethod
    def run_analysis(self):
        ''' runs the analysis including graphing '''

class Line():
    ''' handles the slope, y_int for any lines. ie master line for comparison, and newly calibrated lines for batches'''
    def __init__(self):
        self.slope = None
        self.y_intercept = None
        self.r_squared = None

    def get_values_from_json(self):
        ''' use this one for a master line, where we will grab from JSON'''
        with open('config/master_calibration_parameters.json', 'r', encoding="utf-8") as file:
            params = json.load(file)
        self.slope, self.y_intercept, self.r_squared = params["calibration_parameters"]["slope"], params["calibration_parameters"]["y_intercept"], params["calibration_parameters"]["r_squared"]
        
    def set_values(self, slope: float, y_int: float, r_squared: float):
        ''' use this one if its not the master line, ie the measured line so it can be passed in'''
        self.slope = slope
        self.y_intercept = y_int
        self.r_squared = r_squared


class SubplotAnalysis(Analysis):
    ''' specific analysis with subplots, ie multiple curves for current / counts vs time '''
    def __init__(self, data: Data):
        self.data = data
    def run_analysis(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.axvline(x = 10, linestyle = "dashed", color = "black")
        if self.data.analysis_type == "LactateVSPCalibration":
            ax.set_ylabel("Current (nA)")
            ax.set_ylim(bottom = 0, top = 2000)
        elif self.data.analysis_type == "LactateStoneCalibration":
            ax.set_ylabel("Counts")
            # ax.set_ylim(bottom = 0, top = 2000)
        
        for run in self.data.nested_data:
            x = run.x_axis
            y = run.y_axis
            conc = run.concentration
            ax.plot(x, y, label = conc + " mg/dL")
        ax.legend()
        ax.legend(loc = "lower right")
        ax.legend(fontsize = "xx-small")
        return fig, ax

class LinearityAnalysis(Analysis):
    ''' plots linearity between current / count and conc. '''
    def __init__(self, data):
        self.data = data
        self.currents = []
        self.concentrations = []
        self.find_measurement()

    def find_measurement(self):
        ''' groups concentrations and averages them, to get final averaged conc. and current / count point '''
        # Group runs by concentration
        concentration_groups = {}
        for run in self.data.nested_data:
            if run.concentration in concentration_groups:
                concentration_groups[run.concentration].append(run)
            else:
                concentration_groups[run.concentration] = [run]

        self.currents = []
        self.concentrations = []

        time_point = 10
        for conc, runs in concentration_groups.items():
            avg_currents = []
            for run in runs:
                closest_index = numpy.abs(numpy.array(run.x_axis) - time_point).argmin()
                avg_currents.append(run.y_axis[closest_index])
            avg_current = numpy.mean(avg_currents)
            self.currents.append(avg_current)
            self.concentrations.append(conc)

    def run_analysis(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Concentration (mg/dL)")

        if self.data.analysis_type == "LactateVSPCalibration":
            ax.set_ylabel("Current (nA)")
        elif self.data.analysis_type == "LactateStoneCalibration":
            ax.set_ylabel("Counts")

        x = numpy.array([float(i) for i in self.concentrations])
        y = numpy.array(self.currents, dtype=float)
        ax.scatter(x, y)

        # Calculate the linear regression
        slope, intercept, r_value, _, _ = linregress(x, y)
        line = slope*x + intercept

        # Plot the linear regression line
        ax.plot(x, line, 'r', label=f'y={slope:.2f}x+{intercept:.2f}')

        # if slope != 0:  # To avoid division by zero
        #     ax.plot(x, line, 'g--', label=f'x={(1/slope):.2f}y{-intercept/slope:.2f}')
        # else:
        #     print("Slope is zero, cannot solve for x.")

        new_slope = 1 / slope
        new_int = -intercept / slope
        

        # Calculate and display R^2 value
        r_squared = r_value**2
        ax.text(0.05, 0.75, f'R^2 = {r_squared:.2f}', transform=ax.transAxes)

        ax.legend()

        measured_line = Line()
        measured_line.set_values(new_slope, new_int, r_squared)

        return fig, ax, measured_line
    
class QAAnalysis(Analysis):
    ''' quality assurance analysis, which will take the slope and y intercept from the linearity analysis and compare it to expected values '''
    def __init__(self, measured_line: Line):
        self.measured_line = measured_line
        self.master_line = Line()
        self.master_line.get_values_from_json()
        self.slope_rpd_percent = 5 # TODO later, we load these from a config.json
        self.y_int_rpd_percent = 5 

    def run_analysis(self) -> tuple[bool, bool, bool]:
        slope_check = self.check_slope_rpd(self.master_line.slope, self.measured_line.slope)
        int_check = self.check_y_intercept_rpd(self.master_line.y_intercept, self.measured_line.y_intercept)
        r_squared_check = self.check_r_squared(self.master_line.r_squared, self.measured_line.r_squared)
        return slope_check, int_check, r_squared_check

    def get_rpd(self, true_value: float, measured_value: float) -> float:
        ''' calculates the RPD (relative measure of difference) for any 2 numbers '''
        rpd = abs(true_value - measured_value) / ((true_value + measured_value) / 2) * 100
        return rpd

    def check_slope_rpd(self, master_slope, measured_slope):
        ''' checks if the slope RPD is within 5%, otherwise reject'''
        rpd = self.get_rpd(master_slope, measured_slope)
        if rpd <= self.slope_rpd_percent:
            return True
        print(f"slope failed: {rpd}")
        return False
    
    def check_y_intercept_rpd(self, master_int, measured_int):
        ''' checks if the int RPD is within 5%, otherwise reject'''
        rpd = self.get_rpd(master_int, measured_int)
        if rpd <= self.y_int_rpd_percent:
            return True
        print(f"int failed: {rpd}")
        return False
        
    def check_r_squared(self, master_r_squared, measured_r_squared):
        '''checks if r^2 is above a certain amount'''
        if measured_r_squared < master_r_squared:
            print(f"r failed: {measured_r_squared}")
            return False
        return True


class AnalysisCore():
    
    ''' handles the core functionality tying together the analyses and data handling'''
    def __init__(self, directory: str, analysis_type: str, axis_order_in_file: tuple[str, str] = ('current', 'time')): #this all needs to grab right from UI choices
        self.data = Data(directory, analysis_type, axis_order_in_file)
        self.sp = SubplotAnalysis(self.data)
        self.la = LinearityAnalysis(self.data)
        self.qa = None

    def run(self):
        ''' runs the app '''
        fig1, ax1 = self.sp.run_analysis()
        fig2, ax2, measured_line = self.la.run_analysis()
        self.qa = QAAnalysis(measured_line)
        qa_checks = self.qa.run_analysis()

        return fig1, ax1, fig2, ax2, measured_line, qa_checks
