''' handles the core functionality tying together the menu and the analysis '''
from src.Menu import MainMenu

class Core():
    ''' ties together the menu and analyses '''
    def __init__(self):
        self.menu = MainMenu()

    def run(self):
        ''' runs the app '''
        self.menu.run()


# data = Data("data_020824")
# sp = SubplotAnalysis(data)
# sp.run_analysis()
# la = LinearityAnalysis(data)
# la.run_analysis()