from yaml import Loader

from .BaseController import BaseController
from .ProjectController import ProjectContoroller
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from fastapi import UploadFile
from models import ProcessEnums
import re
import os

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectContoroller().get_project_path(project_id=project_id)

    def get_file_extension(self, file_name: str):

        _ , ext = os.path.splitext(file_name)

        return ext

    def get_file_loader(self, file_name: str):

        file_extension = self.get_file_extension(file_name=file_name)
        file_path = os.path.join(
            self.project_path,
            file_name
        )

        if not os.path.exists(file_path):
            return None

        if file_extension == ProcessEnums.TXT.value:
            return TextLoader(file_path=file_path, encoding="utf-8")
            
        if file_extension == ProcessEnums.PDF.value:
            return PyMuPDFLoader(file_path=file_path)

        return None

    def get_file_content(self, file_name: str): # return list ['content': --, 'metadata':--]

        loader = self.get_file_loader(file_name=file_name)

        if loader:
            return loader.load()

        return None

    def process_file_content(self, file_content: list, file_name: str,
                            chunk_size: int=100, overlap_size: int=20):

        if chunk_size <= 0:
            raise ValueError('chunk_size must be greater than zero')

        if overlap_size < 0 or overlap_size >= chunk_size:
            raise ValueError('overlap_size must be between zero and chunk_size - 1')

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len
        )

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas = file_content_metadata
        )

        return chunks


