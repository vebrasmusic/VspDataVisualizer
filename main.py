import os
import numpy
import matplotlib.pyplot as plt
from scipy.stats import linregress

class Run():
    def __init__(self, file_path):
        self.file_path = file_path
        self.time = None
        self.current = None
        self.concentration = None
        self.load_data()
        self.parse_conc()

    def load_data(self):
        #transpose?
        current, time = numpy.loadtxt(self.file_path, skiprows=1, unpack=True)
        self.adjust_time(time)
        self.current = current * 1E6

    def adjust_time(self, time_array):
        first_time = time_array[0]
        self.time = time_array - first_time


    def parse_conc(self):
        path = self.file_path.name
        conc_split = path.split("_")
        conc = conc_split[0] + "." + conc_split[1]
        self.concentration = conc

class Data():
    #this should only handle mu8ltiple runs, should not know about analyses
    def __init__(self, directory):
        self.directory = directory
        self.nested_data = []
        self.load_data()
        self.sort_data()
        
    def load_data(self):
        for file in os.scandir(self.directory):
            if file.is_file():
                run_obj = Run(file)
                self.nested_data.append(run_obj)

    def sort_data(self):
        self.nested_data = sorted(self.nested_data, key=lambda run: float(run.concentration))


class Analysis():
    # can have a figure, and some rules etc.abs
    # data will ave a couple analyses

    def __init__(self, data):
        self.data = data

    def run_analysis(self):
        pass

class SubplotAnalysis(Analysis):
    def __init__(self, data):
        super().__init__(data)

    def run_analysis(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Current (nA)")
        ax.set_ylim(bottom = 0, top = 2000)
        ax.axvline(x = 10, linestyle = "dashed", color = "black")

        for run in self.data.nested_data:
            x = run.time
            y = run.current
            conc = run.concentration
            ax.plot(x, y, label = conc + " mg/dL")
        ax.legend()
        plt.show()

class LinearityAnalysis(Analysis):
    def __init__(self, data):
        super().__init__(data)
        self.currents = []
        self.concentrations = []
        self.find_measurement()

    def find_measurement(self):
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
                closest_index = numpy.abs(numpy.array(run.time) - time_point).argmin()
                avg_currents.append(run.current[closest_index])
            avg_current = numpy.mean(avg_currents)
            self.currents.append(avg_current)
            self.concentrations.append(conc)

    def run_analysis(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Concentration (mg/dL)")
        ax.set_ylabel("Current (nA)")

        x = numpy.array([float(i) for i in self.concentrations])
        y = numpy.array(self.currents, dtype=float)
        ax.scatter(x, y)

        # Calculate the linear regression
        slope, intercept, r_value, _, _ = linregress(x, y)
        line = slope*x + intercept

        # Plot the linear regression line
        ax.plot(x, line, 'r', label=f'y={slope:.2f}x+{intercept:.2f}')

        # Calculate and display R^2 value
        r_squared = r_value**2
        ax.text(0.05, 0.95, f'R^2 = {r_squared:.2f}', transform=ax.transAxes)

        ax.legend()
        plt.show()


def main():
    data = Data("data_020824")
    sp = SubplotAnalysis(data)
    sp.run_analysis()
    la = LinearityAnalysis(data)
    la.run_analysis()


if __name__ == "__main__":
    main()