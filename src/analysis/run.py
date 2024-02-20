''' defines Run objects and their internal components '''

import os
from abc import ABC, abstractmethod
import numpy


class ConcentrationParser():
    ''' base class for parsing the concentration from the filename '''

    def extract_concentration_from_filename(self, file_path: str) -> str:
        ''' extract the concentration from the filename. this assumes that you
        put int he concentration in the filename. Example would be "4.15 mg/dL",
        which would be represented as "4_15_{any other metadata}.txt".
        '''
        file_name = os.path.basename(file_path)
        conc_split = file_name.split("_")
        conc = conc_split[0] + "." + conc_split[1]
        return conc

class DataModifier(ABC):
    '''
    abstract class for modifying the data,
    such as scaling the current, adjusting the time, etc.
    '''

    @abstractmethod
    def modify_data(self, loaded_data_tuple):
        ''' change the data here. can call things like "scale", etc.'''

    def scale_current(self, current_array):
        ''' scales the current from mA to nA'''
        return current_array * 1E6

class TextLoader(ABC):
    ''' base class for loading data from a text file '''
    @abstractmethod
    def load_data(self, file_path: str) -> tuple[numpy.ndarray, numpy.ndarray]:
        ''' load a single text file into a numpy array ''' 

class LactateVSPCalibrationTextLoader(TextLoader):
    ''' loads the text file data into numpy arrays '''
    def __init__(self, axis_order_in_file: tuple[str, str]):
        self.axis_order_in_file = axis_order_in_file #dependency injection of the axes order from the UI

    def load_data(self, file_path: str) -> tuple[numpy.ndarray, numpy.ndarray]:
        ''' load a single text file into a numpy array based on the axis order specified '''
        # Load the data from the file
        loaded_data = numpy.loadtxt(file_path, skiprows=1, unpack=True)
        
        # Dynamically unpack the loaded data based on the axis_order_in_file
        if self.axis_order_in_file == ('time', 'current'):
            time_array, current_array = loaded_data
        elif self.axis_order_in_file == ('current', 'time'):
            current_array, time_array = loaded_data
        else:
            raise ValueError("Invalid axis order. Must be either ('time', 'current') or ('current', 'time').")
        
        return time_array, current_array


class LactateVSPCalibrationDataModifier(DataModifier):
    ''' concrete implementation of DataModifier for the VSP format '''

    def modify_data(self, loaded_data_tuple):
        time_array, current_array = loaded_data_tuple
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

        #from this unpack, we only want the following: time, count2, count3, stage2 (although thats if we dont use peak detection, whcih we may want to)
        #remember that time now is in ms, need to convert / adjust
        time_array, _, _, count2_array, stage2_array, count3_array, _, _, _, _   = numpy.loadtxt(file_path, skiprows=4, unpack=True) #this line may change, given that we should be able to select from the menu
        
        return time_array, count2_array, stage2_array, count3_array



class LactateStoneCalibrationDataModifier(DataModifier):
    ''' concrtete implementation of data modifier for the lactate stone, which has to find the 3rd stage from the count vs time data '''

    def modify_data(self, loaded_data_tuple):
        time_array, count2_array, stage2_array, count3_array = loaded_data_tuple
        count_array = self.__select_highest_channel(count2_array, count3_array)
        adjusted_time_array, adjusted_count_array = self.__adjust_analysis_window(time_array, count_array, stage2_array)
        readjusted_time_array = self.__adjust_time(adjusted_time_array)
        scaled_time_array = self.__scale_time(readjusted_time_array)
        return scaled_time_array, adjusted_count_array

    def __scale_time(self, time_array: numpy.ndarray) -> numpy.ndarray:
        ''' scales time from ms to s '''
        return time_array / 1000
    
    def __select_highest_channel(self, count2_array: numpy.ndarray, count3_array: numpy.ndarray):
        ''' this finds the max of each, so that u can see which graph is higher. thats the one we choose to continue'''
        max2 = count2_array.max()
        max3 = count3_array.max()
        if max2 > max3:
            return count2_array
        return count3_array
        
    def __adjust_analysis_window(self, time_array: numpy.ndarray, count_array: numpy.ndarray, stage2_array: numpy.ndarray):
        ''' adjust the window by finding where the actual curve starts (stage 3) '''
        measurement_stage_index = 0
        for i, stage in enumerate(stage2_array):
            if stage == 2:
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
    ''' class that handles the data for a single run '''

    def __init__(self, file_path: str, text_loader: TextLoader, data_modifier: DataModifier):
        self.concentration_parser = ConcentrationParser()
        self.concentration = self.concentration_parser.extract_concentration_from_filename(file_path)

        self.file_path = file_path
        self.text_loader = text_loader
        self.data_modifier = data_modifier

        loaded_data_tuple = self.load_data()
        self.x_axis, self.y_axis = self.modify_data(loaded_data_tuple)

    def load_data(self):
        ''' load a single text file into a numpy array '''
        print(self.file_path)
        return self.text_loader.load_data(self.file_path)

    def modify_data(self, output_tuple):
        ''' modify data from the output of the load_data function '''
        return self.data_modifier.modify_data(output_tuple)

class RunFactory():
    ''' programmatically creates all necessary Run for an analysis '''

    def create_run(self, file_path: str, text_loader, data_modifier):
        ''' makes the actual run by combining / returning '''
        run = Run(file_path, text_loader, data_modifier)
        return run

    def return_run(self, analysis_type: str, file_path: str, axis_order_in_file: tuple[str, str] = ('current', 'time')):
        ''' creates all experiment classes for a given analysis type '''
        if analysis_type == "LactateVSPCalibration":
            text_loader = LactateVSPCalibrationTextLoader(axis_order_in_file)
            data_modifier = LactateVSPCalibrationDataModifier()
            return self.create_run(file_path, text_loader, data_modifier)
        if analysis_type == "LactateStoneCalibration":
            text_loader = LactateStoneCalibrationTextLoader()
            data_modifier = LactateStoneCalibrationDataModifier()
            return self.create_run(file_path, text_loader, data_modifier)
        raise ValueError(f"Unknown run type: {analysis_type}")