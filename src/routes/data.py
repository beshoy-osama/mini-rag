from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
import aiofiles
from models import ResponseSignal
from .schemes.data import ProcessRequest
from helpers.configurations import get_settings, Settings
from controllers import DataController, ProjectContoroller, ProcessController
import logging

logger = logging.getLogger('uv-logger')

data_router = APIRouter(
prefix= "/api/v1/data",
tags=['api_v1', 'data']
)

@data_router.post('/upload/{project_id}')
async def upload_file(project_id: str, file: UploadFile,
                        app_settings: Settings = Depends(get_settings)
                        ):

        # validate file properties
        is_valid, signal_result = DataController().validate_upload_file(file=file)

        if not is_valid:
                return JSONResponse(
                        content={
                                'signal': signal_result
                                },
                        status_code=status.HTTP_400_BAD_REQUEST)

        file_path, file_id = DataController().generate_unique_file_path(file_name=file.filename, project_id=project_id)

        try:
                async with aiofiles.open(file_path, "wb") as f:
                        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                                await f.write(chunk)
        except Exception as e:

                logger.error(f'error while uploading file: {e}')

                return JSONResponse(
                                content={
                                        'response signal': ResponseSignal.FILE_UPLOADED_FAILED.value
                                                },
                                                status_code=status.HTTP_400_BAD_REQUEST
                                                )

        return JSONResponse(
                content={
                        'response signal': ResponseSignal.FILE_UPLOADED_SUCCESS.value,
                        'file_id': file_id
                                }
                                )

@data_router.post('/process/{project_id}')
async def process_endpoint(project_id: str, process_request: ProcessRequest):

        file_id = process_request.file_id
        chunk_size = process_request.chunk_size
        overlap_size = process_request.overlap_size

        process_controller = ProcessController(project_id=project_id)

        file_content = process_controller.get_file_content(file_name=file_id)

        file_chunks = process_controller.process_file_content(
                file_content=file_content, 
                file_name=file_id,
                chunk_size=chunk_size,
                overlap_size=overlap_size)
        

        if file_chunks == None or len(file_chunks) == 0:
                return JSONResponse(
                content={
                        'response signal': ResponseSignal.PROCESSING_FAILED.value
                                },
                                status_code=status.HTTP_400_BAD_REQUEST
                                )

        return file_chunks
                                        

