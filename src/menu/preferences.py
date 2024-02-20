''' defines preferences singleton classes, allows for changing / reading of prefs etc. '''

import json

class Preferences:
    ''' singleton class that holds all the preferences, loads form file etc.'''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating new Preferences instance")
            cls._instance = super(Preferences, cls).__new__(cls)
            cls._instance.load_preferences()
        else:
            print("Using existing Preferences instance")
        return cls._instance

    def load_preferences(self):
        ''' loads the preferences from the preferences.json file '''
        try:
            with open("config/preferences.json", "r", encoding="utf-8") as f:
                self.preferences = json.load(f)
        except FileNotFoundError:
            self.preferences = {}

    def get_preference(self, category: str, key: str, default={}) -> str:
        ''' gets a preference from the preferences dict, if it doesn't exist, returns the default '''
        category_dict = self.preferences.get(category, default)
        value = category_dict.get(key, default)
        return value
    
    def save_preferences(self):
        ''' saves the preferences to the json file config/preferences.json '''
        with open("config/preferences.json", "w", encoding="utf-8") as f:
            json.dump(self.preferences, f)

    
