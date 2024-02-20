''' defines preferences singleton classes, allows for changing / reading of prefs etc. '''

import json

class Preferences:
    ''' singleton class that holds all the preferences, loads form file etc.'''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Preferences, cls).__new__(cls)
            cls._instance.load_preferences()
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

class PreferenceChanges():
    ''' singleton class that holds any changes made to the Preferences before saving.'''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PreferenceChanges, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        ''' init for the singleotn '''
        self.changes = {}

    def add_change(self, new_value: str, category: str, key: str):
        ''' adds a change to the change dict '''
        if category in self.changes:
            self.changes[category][key] = new_value
        else:
            self.changes[category] = {key: new_value}





    
