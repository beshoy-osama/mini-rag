from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import aiofiles
from numpy import number
from models import ChunkModel,ProjectModel ,ResponseSignal
from models.db_schemes.data_chunk import DataChunk
from .schemes.data import ProcessRequest
from helpers.configurations import get_settings, Settings
from controllers import DataController, ProcessController
import logging


logger = logging.getLogger('uv-logger')

data_router = APIRouter(
prefix= "/api/v1/data",
tags=['api_v1', 'data']
)

# Upload file endpoint
@data_router.post('/upload/{project_id}')
async def upload_file(request: Request, project_id: str, file: UploadFile,
                        app_settings: Settings = Depends(get_settings)
                        ):
        project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)  # Initialize ProjectModel with the database client

        await project_model.get_project_or_create_one(project_id=project_id)  # Get or create the project

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

# Process file endpoint
@data_router.post('/process/{project_id}')
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

        file_id = process_request.file_id
        chunk_size = process_request.chunk_size
        overlap_size = process_request.overlap_size
        do_reset = process_request.do_reset

        project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)  # Initialize ProjectModel with the database client

        project = await project_model.get_project_or_create_one(project_id=project_id)  # Get or create the project


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

        
        file_chunks_record = [
                DataChunk(
                        chunk_text=chunk.page_content,
                        chunk_metadata=chunk.metadata,
                        chunk_order=index+1,
                        chunk_project_id=project.id
                ) for index, chunk in enumerate(file_chunks)

        ]

        
        chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)  # Initialize ChunkModel with the database client

        if do_reset == 1:
                await chunk_model.delete_chunks_by_project_id(project_id=project.id)


        number_of_chunks_inserted = await chunk_model.insert_many_chunks(chunks=file_chunks_record)

        return JSONResponse(
                content={
                        'response signal': ResponseSignal.PROCESSING_SUCCESS.value,
                        'number_of_chunks_inserted': number_of_chunks_inserted
                                }
        )

