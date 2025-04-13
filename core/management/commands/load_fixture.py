import json
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load fixture for assessment fixtures"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Start Loading assessment fixtures"))
        self.save_data_to_db("fixture.json")

    def load_json_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: The file '{file_path}' was not found."))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"Error: The file '{file_path}' is not a valid JSON file."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {str(e)}"))

    def save_data_to_db(self, file_name):
        # Construct the full path to the fixture.json file
        full_path = os.path.join(os.path.dirname(__file__), file_name)  # Get the directory of the current file
        self.stdout.write(self.style.SUCCESS(f"Loading data from: {full_path}"))
        data = self.load_json_file(full_path)
        if data is not None:
            print(data)
        else:
            self.stdout.write(self.style.ERROR(f"Failed to load data from '{full_path}'."))
