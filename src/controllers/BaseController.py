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

    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

