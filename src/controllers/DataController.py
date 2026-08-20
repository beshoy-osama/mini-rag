from .BaseController import BaseController
from .ProjectController import ProjectContoroller
from fastapi import UploadFile
from models import ResponseSignal
import re
import os


class DataController(BaseController):
    def __init__ (self):
        super().__init__()
        self.size_scale = 1048576

    ############### To_get_file_size ##################
    def get_file_size(self, file: UploadFile) -> int:
        if file.size is not None:
            return file.size

        # Some upload backends do not provide `size`; calculate it from the stream.
        current_position = file.file.tell()
        file.file.seek(0, 2)
        calculated_size = file.file.tell()
        file.file.seek(current_position)

        return calculated_size
    ####################################################

    def validate_upload_file(self, file: UploadFile):


        file_size = self.get_file_size(file)

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file_size > (self.app_settings.FILE_MAX_SIZE * self.size_scale):
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_UPLOADED_SUCCESS.value

    def generate_unique_file_path(self, file_name: str, project_id: str):

        random_key = self.generate_random_string()

        project_path = ProjectContoroller().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(file_name=file_name)

        stem, ext = os.path.splitext(cleaned_file_name)

        new_file_path = os.path.join(
            project_path,
            random_key + '_' + stem + ext
        )

        while os.path.exists(new_file_path):

            random_key = self.generate_random_string()

            new_file_path = os.path.join(
                project_path,
                random_key + '_' + stem + ext
            )

        file_id = random_key + '_' + stem + ext

        return new_file_path, file_id


    def get_clean_file_name(self, file_name: str):

        # Replace whitespace with underscore first
        cleaned_file_name = re.sub(r'\s+', '_', file_name.strip())
        
        # Remove any character that is not alphanumeric, underscore, or period
        cleaned_file_name = re.sub(r'[^\w.]', '', cleaned_file_name)

        return cleaned_file_name
