from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Convert MB to bytes

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED
        
        if file.size > self.app_settings.MAX_FILE_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED
        
        return True, ResponseSignal.FILE_VALIDATED_SUCCESS
    
    def get_clean_filename(self, orig_filename: str):
        # Remove special characters and spaces
        clean_name = re.sub(r'[^\w]', '', orig_filename.strip())
        clean_name = clean_name.replace(" ", "_")
        return clean_name

    def generate_unique_filepath(self, orig_filename: str, project_id: str):
        random_filename = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        clean_file_name = self.get_clean_filename(
            orig_filename=orig_filename
        )

        new_file_path = os.path.join(
            project_path,
            random_filename + "_" + clean_file_name 
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            random_key = random_key + "_" + clean_file_name
            new_file_path = os.path.join(
                project_path, 
                random_key
            )
        
        return new_file_path, random_key
