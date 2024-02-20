''' defines Data objects '''
import os
from src.analysis.run import RunFactory

class Data():
    ''' handles multiple Run objects, but as a container '''
    #this should only handle mu8ltiple runs, should not know about analyses
    def __init__(self, directory: str, analysis_type: str, axis_order_in_file: tuple[str, str] = ('current', 'time')):
        self.directory = directory
        self.analysis_type = analysis_type
        self.nested_data = []
        self.run_factory = RunFactory()
        self.load_data(axis_order_in_file)
        self.sort_data()

    def load_data(self, axis_order_in_file):
        ''' loads data thru all Run objects '''
        for file in os.scandir(self.directory):
            if file.is_file() and not file.name.startswith('.'): # you can access the str name of the file path using file.path. also ignores hidden files like . ds store
                run_obj = self.run_factory.return_run(self.analysis_type, file.path, axis_order_in_file)
                self.nested_data.append(run_obj)

    def sort_data(self):
        ''' sorts run objects by their concentration / count, lowest to highest '''
        self.nested_data = sorted(self.nested_data, key=lambda run: float(run.concentration))