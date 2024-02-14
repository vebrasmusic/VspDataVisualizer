''' handles the analysis of the data '''
import os
from abc import ABC, abstractmethod
import numpy
import matplotlib.pyplot as plt
from scipy.stats import linregress

'''
Hows this work?


Top level, you have an Analysis, which will run a specific type of analysis / plot data.
An Analysis has a Data object
A Data object has a list of Run objects
A Run can contain different kinds of TextLoader or ConcentrationParser.
'''



class ConcentrationParser():
    ''' base class for parsing the concentration from the filename '''

    def extract_concentration_from_filename(self, file_name: str) -> str:
        ''' extract the concentration from the filename. this assumes that you
        put int he concentration in the filename. Example would be "4.15 mg/dL",
        which would be represented as "4_15_{any other metadata}.txt".
        '''
        conc_split = file_name.split("_")
        conc = conc_split[0] + "." + conc_split[1]
        return conc
    


class DataModifier(ABC):
    '''
    abstract class for modifying the data,
    such as scaling the current, adjusting the time, etc.
    '''

    @abstractmethod
    def modify_data(self):
        ''' change the data here. can call things like "scale", etc.'''

    def scale_current(self, current_array):
        ''' scales the current from mA to nA'''
        return current_array * 1E6



class TextLoader(ABC):
    ''' base class for loading data from a text file '''
    @abstractmethod
    def load_data(self, file_path):
        ''' load a single text file into a numpy array ''' 



class LactateVSPCalibrationTextLoader(TextLoader):
    ''' concrete implementation of TextLoader for the VSP format,
    which will take / plot graphs of current vs. concentration
    '''

    def load_data(self, file_path: str):
        ''' load a single text file into a numpy array '''
        current_array, time_array = numpy.loadtxt(file_path, skiprows=1, unpack=True) #this line may change, given that we should be able to select from the menu
        return current_array, time_array
    


class LactateVSPCalibrationDataModifier(DataModifier):
    ''' concrete implementation of DataModifier for the VSP format '''

    def modify_data(self, time_array, current_array):
        new_time_array = self.__adjust_time(time_array)
        new_current_array = self.__scale_current(current_array)
        return new_time_array, new_current_array

    def __scale_current(self, current_array):
        return super().scale_current(current_array)
    
    def __adjust_time(self, time_array):
        '''adjusts time array so that the first time is set as 0'''
        first_time = time_array[0]
        return time_array - first_time
    


class LactateStoneCalibrationTextLoader(TextLoader):
    ''' concrete implementation of TextLoader for the calibration stone setup,
    which will take / plot graphs of count vs. concentration
    '''

    def load_data(self, file_path: str):
        ''' load a single text file into a numpy array '''
        array_list = [
            # AT SOME POINT GET TO THIS
        ]

        #from this unpack, we only want the following: time, count2, count3, stage2 (although thats if we dont use peak detection, whcih we may want to)
        #remember that time now is in ms, need to convert / adjust
        time_array, count1_array, stage1_array, count2_array, stage2_array, count3_array,stage3_array, current1_array, current2_array, current3_array   = numpy.loadtxt(file_path, skiprows=4, unpack=True) #this line may change, given that we should be able to select from the menu
        
        return time_array, count2_array, stage2_array, count3_array



class LactateStoneCalibrationDataModifier(DataModifier):

    def modify_data(self, time_array: numpy.ndarray, count2_array: numpy.ndarray, stage2_array: numpy.ndarray, count3_array: numpy.ndarray):
        count_array = self.__select_highest_channel(count2_array, count3_array)
        adjusted_time_array, adjusted_count_array = self.__adjust_analysis_window(time_array, count_array, stage2_array)
        readjusted_time_array = self.__adjust_time(adjusted_time_array)
        scaled_time_array = self.__scale_time(readjusted_time_array)
        return scaled_time_array, adjusted_count_array

    def __scale_time(self, time_array: numpy.ndarray) -> numpy.ndarray:
        ''' scales time from ms to s '''
        return time_array / 1000
    
    def __select_highest_channel(self, count2_array, count3_array):
        ''' this finds the max of each, so that u can see which graph is higher. thats the one we choose to continue'''
        max2 = count2_array.maximum()
        max3 = count3_array.maximum()
        if max2 > max3:
            return count2_array
        return count3_array
        
    def __adjust_analysis_window(self, time_array: numpy.ndarray, count_array: numpy.ndarray, stage2_array: numpy.ndarray):
        ''' adjust the window by finding where the actual curve starts (stage 3) '''
        measurement_stage_index = 0
        for i in range(len(stage2_array)):
            if stage2_array[i] == 3:
                measurement_stage_index = i
                break
            print("no stage 3 found, error")
        adjusted_time_array = time_array[measurement_stage_index:]
        adjusted_count_array = count_array[measurement_stage_index:]
        return adjusted_time_array, adjusted_count_array

    def __adjust_time(self, time_array: numpy.ndarray) -> numpy.ndarray:
        '''adjusts time array so that the first time is set as 0'''
        first_time = time_array[0]
        return time_array - first_time


class Run():
    ''' base class that handles the data for a single run '''

    def __init__(self, file_path, text_loader: TextLoader, data_modifier: DataModifier):
        self.concentration_parser = ConcentrationParser()
        self.text_loader = text_loader
        self.data_modifier = data_modifier
        self.file_path = file_path
        self.concentration = None
        self.time = None
        self.current = None

    def load_data(self):
        ''' load a single text file into a numpy array '''
        self.text_loader.load_data(self.file_path)


class Data():
    ''' handles multiple Run objects, but as a container '''
    #this should only handle mu8ltiple runs, should not know about analyses
    def __init__(self, directory, run_factory: RunFactory):
        self.directory = directory
        self.run_class = run_class
        self.nested_data = []
        self.load_data()
        self.sort_data()

    def load_data(self):
        ''' loads data thru all Run objects '''
        for file in os.scandir(self.directory):
            if file.is_file():
                run_obj = run_class(file.path)
                self.nested_data.append(run_obj)

    def sort_data(self):
        self.nested_data = sorted(self.nested_data, key=lambda run: float(run.concentration))

class Analysis(ABC):
    # can have a figure, and some rules etc.abs
    # data will ave a couple analyses
    @abstractmethod
    def run_analysis(self):
        pass

class VSPRun(AbstractRun):
    ''' Contains the data for a single run, including conversion from mA to nA '''
    def __init__(self, file_path):
        super().__init__(file_path)
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

class AnalysisCore():
    
    ''' handles the core functionality tying together the analyses and data handling'''
    def __init__(self, directory):
        self.data = Data(directory)
        self.sp = SubplotAnalysis(self.data)
        self.la = LinearityAnalysis(self.data)
        

    def run(self):
        ''' runs the app '''
        self.sp.run_analysis()
        self.la.run_analysis()
