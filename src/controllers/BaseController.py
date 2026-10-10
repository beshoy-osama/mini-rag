from helpers.configurations import get_settings
import os
import string
import random

class BaseController():

    def __init__ (self):

        self.app_settings = get_settings()

        self.base_dir = os.path.dirname(os.path.dirname(__file__))  # src dir

        self.files_dir = os.path.join(  # files dir
            self.base_dir,
            "assets/files"
        )

        self.database_dir = os.path.join(  # database dir
            self.base_dir,
            "assets/database"
        )

    def get_or_create_database_path(self, database_name: str):

            database_path = os.path.join(
                self.database_dir,
                database_name
            )
            
            if not os.path.exists(database_path):
                os.makedirs(database_path, exist_ok=True)

            return database_path

    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

