"""
Module for managing pregnancy-related datasets and FAQs.
"""

import pandas as pd

class DatasetManager:
    def __init__(self, data_filepath):
        self.data_filepath = data_filepath
        self.dataset = self.load_data()

    def load_data(self):
        """ Load the dataset from the specified file path. """
        try:
            data = pd.read_csv(self.data_filepath)
            return data
        except FileNotFoundError:
            print(f"Error: The file {self.data_filepath} was not found.")
            return None

    def get_faq(self):
        """ Return FAQs related to pregnancy management. """
        faqs = {
            'Q1': 'What is the recommended diet during pregnancy?',
            'A1': 'A balanced diet rich in fruits, vegetables, whole grains, and lean proteins is essential.',
            'Q2': 'How much folic acid should I take?',
            'A2': 'At least 400 micrograms per day, starting before pregnancy and continuing during the first trimester.',
            'Q3': 'What are the signs of complications during pregnancy?',
            'A3': 'Unusual bleeding, severe headache, and swelling are signs to consult a doctor.'
        }
        return faqs

    def display_data(self):
        """ Display the loaded dataset. """
        if self.dataset is not None:
            print(self.dataset)
        else:
            print("No data available.")

# Example usage:
# manager = DatasetManager('path/to/dataset.csv')
# manager.display_data()
# faqs = manager.get_faq()
# print(faqs)